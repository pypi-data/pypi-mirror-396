import logging
from typing import Any
from typing import List
from typing import Set

from django_bulk_hooks.dispatcher_preloader import RelationshipPreloader

logger = logging.getLogger(__name__)


class ConditionAnalyzer:
    """Analyzes hook conditions to extract relationship dependencies."""

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.preloader = RelationshipPreloader(model_cls)

    def extract_relationships(self, condition) -> Set[str]:
        """
        Extract relationship paths that a condition might access.

        Args:
            condition: HookCondition instance

        Returns:
            Set of relationship field names to preload
        """
        if not self._is_valid_condition(condition):
            return set()

        relationships = set()

        # Extract from field attribute
        if hasattr(condition, "field"):
            relationships.update(self._extract_from_field(condition.field))

        # Handle composite conditions (AND, OR)
        if hasattr(condition, "cond1") and hasattr(condition, "cond2"):
            relationships.update(self.extract_relationships(condition.cond1))
            relationships.update(self.extract_relationships(condition.cond2))

        # Handle NOT conditions
        if hasattr(condition, "cond"):
            relationships.update(self.extract_relationships(condition.cond))

        return relationships

    def _is_valid_condition(self, condition) -> bool:
        """Check if object is a valid condition (not a Mock or invalid type)."""
        return hasattr(condition, "check") and not hasattr(condition, "_mock_name")

    def _extract_from_field(self, field_path: str) -> Set[str]:
        """Extract relationships from a field path (e.g., 'status__value' -> 'status')."""
        if not isinstance(field_path, str):
            return set()

        relationships = set()

        if "__" in field_path:
            # Extract first part: "status__value" -> "status"
            rel_field = field_path.split("__")[0]
        else:
            rel_field = field_path

        # Normalize FK field names: business_id -> business
        rel_field = self._normalize_fk_field(rel_field)

        # Only add if it's actually a relationship
        if self.preloader.is_relationship_field(rel_field):
            relationships.add(rel_field)

        return relationships

    def _normalize_fk_field(self, field_name: str) -> str:
        """Convert FK field names (business_id -> business) if applicable."""
        if field_name.endswith("_id"):
            potential_field = field_name[:-3]
            if self.preloader.is_relationship_field(potential_field):
                return potential_field
        return field_name


class HookExecutor:
    """Handles individual hook execution with condition checking and preloading."""

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.preloader = RelationshipPreloader(model_cls)
        self.condition_analyzer = ConditionAnalyzer(model_cls)

    def execute(
        self,
        handler_cls,
        method_name: str,
        condition,
        changeset,
        event: str,
    ) -> None:
        """
        Execute a single hook with proper preloading and condition checking.

        Args:
            handler_cls: Hook handler class
            method_name: Method name to call
            condition: Optional condition to filter records
            changeset: ChangeSet with record changes
            event: Hook event name
        """
        # Create handler instance
        handler = self._create_handler_instance(handler_cls)
        method = getattr(handler, method_name)

        # Preload relationships from method decorators
        self._preload_method_relationships(handler, method, changeset, event)

        # Preload relationships from conditions
        if condition and not changeset.operation_meta.get("relationships_preloaded"):
            self._preload_condition_relationships(condition, changeset)

        # Apply condition filter if present
        filtered_changeset = self._apply_condition_filter(
            condition,
            changeset,
            handler_cls,
            method_name,
        )

        if filtered_changeset is None:
            return  # No records passed condition

        # Execute the hook
        self._invoke_hook_method(
            method,
            filtered_changeset,
            handler_cls,
            method_name,
        )

    def _create_handler_instance(self, handler_cls):
        """Create hook handler instance using DI factory."""
        from django_bulk_hooks.factory import create_hook_instance

        return create_hook_instance(handler_cls)

    def _preload_method_relationships(
        self,
        handler,
        method,
        changeset,
        event: str,
    ) -> None:
        """Preload relationships specified in method decorators."""
        # Check for @select_related decorator
        preload_func = getattr(method, "_select_related_preload", None)
        if not preload_func:
            logger.debug("No @select_related decorator found on method")
            return

        try:
            # Mirror logs to dispatcher module logger for test visibility
            try:
                from django_bulk_hooks.dispatcher import logger as _dispatcher_logger  # type: ignore
            except Exception:  # pragma: no cover - fallback if import-time issues
                _dispatcher_logger = None

            # Get the list of fields being preloaded
            fields = getattr(method, "_select_related_fields", ())

            model_cls_override = getattr(handler, "model_cls", None)
            skip_fields = changeset.operation_meta.get("fk_fields_being_updated", set())

            _msg = f"METHOD PRELOAD: @select_related fields: {fields}, model: {changeset.model_cls.__name__}, event: {event}"
            logger.info(_msg)
            if _dispatcher_logger:
                _dispatcher_logger.info(_msg)

            # Preload for new_records
            if changeset.new_records:
                _msg = f"METHOD PRELOAD: Preloading for {len(changeset.new_records)} new records"
                logger.info(_msg)
                if _dispatcher_logger:
                    _dispatcher_logger.info(_msg)
                preload_func(
                    changeset.new_records,
                    model_cls=model_cls_override,
                    skip_fields=skip_fields,
                )

            # Preload for old_records
            if changeset.old_records:
                _msg = f"METHOD PRELOAD: Preloading for {len(changeset.old_records)} old records"
                logger.info(_msg)
                if _dispatcher_logger:
                    _dispatcher_logger.info(_msg)
                preload_func(
                    changeset.old_records,
                    model_cls=model_cls_override,
                    skip_fields=skip_fields,
                )

            changeset.operation_meta["relationships_preloaded"] = True

        except Exception as e:
            logger.warning(f"Failed to preload relationships for method: {e}", exc_info=True)

    def _preload_condition_relationships(self, condition, changeset) -> None:
        """Preload relationships required by condition."""
        relationships = self.condition_analyzer.extract_relationships(condition)
        if not relationships:
            return

        logger.info(f"CONDITION PRELOAD: Preloading relationships: {relationships}")

        if changeset.new_records:
            self.preloader.preload_for_records(
                changeset.new_records,
                relationships,
                preserve_fk_values=True,
            )

        if changeset.old_records:
            self.preloader.preload_for_records(
                changeset.old_records,
                relationships,
                preserve_fk_values=False,
            )

    def _apply_condition_filter(self, condition, changeset, handler_cls, method_name):
        """Apply condition filter to changeset if condition is present."""
        if not condition:
            return changeset

        # Filter change records based on condition
        filtered_changes = []
        for change in changeset.changes:
            # Prefer passing changeset; fall back to legacy signature if unsupported
            try:
                passes = condition.check(change.new_record, change.old_record, changeset=changeset)
            except TypeError:
                passes = condition.check(change.new_record, change.old_record)

            if passes:
                filtered_changes.append(change)

        if not filtered_changes:
            return None

        # Build filtered changeset
        from django_bulk_hooks.changeset import ChangeSet

        filtered = ChangeSet(
            changeset.model_cls,
            filtered_changes,
            changeset.operation_type,
            dict(changeset.operation_meta),
        )
        return filtered

    def _invoke_hook_method(self, method, changeset, handler_cls, method_name) -> None:
        """Invoke the hook method with best-effort signature handling."""
        try:
            # Try new signature first
            method(changeset=changeset, new_records=changeset.new_records, old_records=changeset.old_records)
        except TypeError:
            try:
                # Fallback to legacy signature
                method(new_records=changeset.new_records, old_records=changeset.old_records)
            except Exception as e:
                logger.error(f"Hook execution failed for {handler_cls.__name__}.{method_name}: {e}")
                raise
