"""
Bulk operation coordinator - Single entry point for all bulk operations.

This facade hides the complexity of wiring up multiple services and provides
a clean, simple API for the QuerySet to use.
"""

import logging
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from django.core.exceptions import FieldDoesNotExist
from django.db import connections
from django.db import transaction
from django.db.models import Model
from django.db.models import QuerySet

from django_bulk_hooks.changeset import ChangeSet
from django_bulk_hooks.changeset import RecordChange
from django_bulk_hooks.context import get_bypass_hooks
from django_bulk_hooks.helpers import build_changeset_for_create
from django_bulk_hooks.helpers import build_changeset_for_delete
from django_bulk_hooks.helpers import build_changeset_for_update
from django_bulk_hooks.helpers import extract_pks

logger = logging.getLogger(__name__)


@dataclass
class InstanceSnapshot:
    """Snapshot of instance state for modification tracking."""

    field_values: Dict[str, Any]


class BulkOperationCoordinator:
    """
    Single entry point for coordinating bulk operations.

    This coordinator manages all services and provides a clean facade
    for the QuerySet. It wires up services and coordinates the hook
    lifecycle for each operation type.

    Services are created lazily and cached for performance.
    """

    # Constants
    UPSERT_TIMESTAMP_THRESHOLD_SECONDS = 1.0

    def __init__(self, queryset: QuerySet):
        """
        Initialize coordinator for a queryset.

        Creates a fresh dispatcher context for this operation,
        following Salesforce's per-transaction trigger context pattern.
        Each operation gets isolated state that's automatically cleaned up.

        Args:
            queryset: Django QuerySet instance
        """
        self.queryset = queryset
        self.model_cls = queryset.model

        # Lazy-initialized services
        self._analyzer = None
        self._record_classifier = None
        self._executor = None

        # Dispatcher is per-coordinator (Salesforce pattern)
        # Each operation gets a fresh context, automatically GC'd when done
        self._dispatcher = None

        # Cache for old records in upsert operations
        self._upsert_old_records_map = None

    def __del__(self):
        """
        Cleanup coordinator state when garbage collected.

        Ensures memory is freed even if the coordinator instance
        lingers beyond its intended lifetime. This is a safety net
        for proper resource cleanup.
        """
        self._cleanup()

    def _cleanup(self):
        """
        Clear all cached state to enable garbage collection.

        Explicitly clears references to potentially large objects:
        - Upsert cache (can hold thousands of model instances)
        - Service references (to break circular references)
        """
        # Clear upsert cache (can hold thousands of model instances)
        self._upsert_old_records_map = None

        # Clear service references to break circular references
        self._analyzer = None
        self._record_classifier = None
        self._executor = None
        self._dispatcher = None

    def _close_connection(self) -> None:
        """
        Explicitly close database connection to return it to the pool.

        CRITICAL: This prevents connection leaks in long-running processes
        (Celery tasks, management commands, async workers) by immediately
        returning the connection to the pool instead of waiting for:
        - CONN_MAX_AGE timeout (default: persistent connections)
        - Worker process termination
        - Garbage collection

        Multi-database Support:
        - Uses the specific database connection for this queryset
        - Safe to call on already-closed connections (idempotent)
        - Works with all connection pooling backends (PgBouncer, pgpool, etc.)

        Performance Impact:
        - Negligible: Just returns connection to pool
        - Benefit: Prevents connection accumulation under concurrent load

        Context:
        - Web requests: Modest improvement (faster pool returns)
        - Celery tasks: Critical (prevents "too many connections" errors)
        - Management commands: Good (prevents long-held connections)
        """
        try:
            db_alias = self.queryset.db
            connection = connections[db_alias]
            connection.close()
            logger.debug(
                "Closed database connection '%s' for %s operation",
                db_alias,
                self.model_cls.__name__,
            )
        except Exception as e:
            # Log but don't raise - connection cleanup failure should not
            # break the operation (which already completed successfully)
            logger.warning(
                "Failed to close database connection for %s: %s",
                self.model_cls.__name__,
                e,
                exc_info=True,
            )

    # ==================== SERVICE PROPERTIES ====================

    def _get_or_create_service(self, service_name: str, service_class: type, *args, **kwargs) -> Any:
        """
        Generic lazy service initialization with caching.

        Args:
            service_name: Name of the service attribute (e.g., 'analyzer')
            service_class: The class to instantiate
            *args, **kwargs: Arguments to pass to the service constructor

        Returns:
            The service instance
        """
        attr_name = f"_{service_name}"
        service = getattr(self, attr_name)

        if service is None:
            service = service_class(*args, **kwargs)
            setattr(self, attr_name, service)

        return service

    @property
    def analyzer(self):
        """Get or create ModelAnalyzer."""
        from django_bulk_hooks.operations.analyzer import ModelAnalyzer

        return self._get_or_create_service("analyzer", ModelAnalyzer, self.model_cls)

    @property
    def record_classifier(self):
        """Get or create RecordClassifier."""
        from django_bulk_hooks.operations.record_classifier import RecordClassifier

        return self._get_or_create_service("record_classifier", RecordClassifier, self.model_cls)

    @property
    def executor(self):
        """Get or create BulkExecutor."""
        from django_bulk_hooks.operations.bulk_executor import BulkExecutor

        return self._get_or_create_service(
            "executor",
            BulkExecutor,
            queryset=self.queryset,
            analyzer=self.analyzer,
            record_classifier=self.record_classifier,
        )

    @property
    def dispatcher(self):
        """
        Get or create Dispatcher for this operation.

        Following Salesforce's pattern: each operation gets an isolated
        dispatcher context that's automatically cleaned up when the
        coordinator is garbage collected.
        """
        if self._dispatcher is None:
            from django_bulk_hooks.registry import get_registry
            from django_bulk_hooks.dispatcher import HookDispatcher

            self._dispatcher = HookDispatcher(get_registry())

        return self._dispatcher

    @property
    def model_classes(self) -> List[type]:
        """Return list containing only the current model class."""
        return [self.model_cls]

    # ==================== PUBLIC API ====================

    @transaction.atomic
    def create(
        self,
        objs: List[Model],
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        update_fields: Optional[List[str]] = None,
        unique_fields: Optional[List[str]] = None,
        bypass_hooks: bool = False,
    ) -> List[Model]:
        """
        Execute bulk create with hooks.

        Args:
            objs: List of model instances to create
            batch_size: Number of objects per batch
            ignore_conflicts: Ignore conflicts if True
            update_conflicts: Update on conflict if True
            update_fields: Fields to update on conflict
            unique_fields: Fields to check for conflicts
            bypass_hooks: Skip all hooks if True

        Returns:
            List of created objects
        """
        try:
            if not objs:
                return objs

            self.analyzer.validate_for_create(objs)

            # Handle upsert classification upfront
            existing_record_ids, existing_pks_map = self._classify_upsert_records(objs, update_conflicts, unique_fields)

            # Fetch old records BEFORE the operation for upsert change detection
            # This is critical for HasChanged conditions in after_update hooks
            if update_conflicts and existing_pks_map:
                existing_pks = list(existing_pks_map.values())
                # Query database directly for old records before they're modified
                old_records = self.model_cls._base_manager.filter(pk__in=existing_pks)
                self._upsert_old_records_map = {obj.pk: obj for obj in old_records}
            else:
                self._upsert_old_records_map = None

            changeset = build_changeset_for_create(
                self.model_cls,
                objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
            )

            def operation():
                return self.executor.bulk_create(
                    objs,
                    batch_size=batch_size,
                    ignore_conflicts=ignore_conflicts,
                    update_conflicts=update_conflicts,
                    update_fields=update_fields,
                    unique_fields=unique_fields,
                    existing_record_ids=existing_record_ids,
                    existing_pks_map=existing_pks_map,
                )

            return self._execute_with_hooks(
                changeset=changeset,
                operation=operation,
                event_prefix="create",
                bypass_hooks=bypass_hooks,
            )
        finally:
            # CRITICAL: Return database connection to pool immediately
            # Prevents connection leaks in Celery tasks and long-running processes
            self._close_connection()

    @transaction.atomic
    def update(
        self,
        objs: List[Model],
        fields: List[str],
        batch_size: Optional[int] = None,
        bypass_hooks: bool = False,
    ) -> int:
        """
        Execute bulk update with hooks.

        Args:
            objs: List of model instances to update
            fields: List of field names to update
            batch_size: Number of objects per batch
            bypass_hooks: Skip all hooks if True

        Returns:
            Number of objects updated
        """
        try:
            # DEBUG: Log incoming fields parameter
            logger.debug(f"🟧 COORDINATOR.update ENTRY: fields={fields}, objs count={len(objs)}")

            if not objs:
                return 0

            self.analyzer.validate_for_update(objs)

            # DEBUG: Log what we're about to update
            for obj in objs:
                logger.debug(f"🔵 BULK_UPDATE: About to fetch old records for {obj.__class__.__name__} pk={obj.pk}")
                for field in fields:
                    field_id = f"{field}_id" if not field.endswith("_id") else field
                    if hasattr(obj, field_id):
                        value = obj.__dict__.get(field_id)
                        logger.debug(f"🔵 BULK_UPDATE: Current {field_id}={value} in new instance")

            old_records_map = self.analyzer.fetch_old_records_map(objs)

            # DEBUG: Log what we fetched from the database
            for pk, old_obj in old_records_map.items():
                logger.debug(f"🟢 OLD_RECORD_FETCHED: {old_obj.__class__.__name__} pk={pk}")
                for field in fields:
                    field_id = f"{field}_id" if not field.endswith("_id") else field
                    if hasattr(old_obj, field_id):
                        value = old_obj.__dict__.get(field_id)
                        logger.debug(f"🟢 OLD_RECORD_FETCHED: {field_id}={value} from database")

            changeset = self._build_update_changeset(objs, fields, old_records_map)

            logger.debug(f"🟧 COORDINATOR.update: About to call executor with fields={fields}")

            def operation():
                logger.debug(f"🟧 COORDINATOR.update OPERATION: Calling executor.bulk_update with fields={fields}")
                return self.executor.bulk_update(objs, fields, batch_size=batch_size)

            return self._execute_with_hooks(
                changeset=changeset,
                operation=operation,
                event_prefix="update",
                bypass_hooks=bypass_hooks,
            )
        finally:
            # CRITICAL: Return database connection to pool immediately
            # Prevents connection leaks in Celery tasks and long-running processes
            self._close_connection()

    @transaction.atomic
    def update_queryset(
        self,
        update_kwargs: Dict[str, Any],
        bypass_hooks: bool = False,
    ) -> int:
        """
        Execute queryset.update() with full hook support.

        ARCHITECTURE & PERFORMANCE TRADE-OFFS
        ======================================

        To support hooks with queryset.update(), we must:
        1. Fetch old state (SELECT all matching rows)
        2. Execute database update (UPDATE in SQL)
        3. Fetch new state (SELECT all rows again)
        4. Run VALIDATE_UPDATE hooks (validation only)
        5. Run BEFORE_UPDATE hooks (CAN modify instances)
        6. Persist BEFORE_UPDATE modifications (bulk_update)
        7. Run AFTER_UPDATE hooks (read-only side effects)

        Performance Cost:
        - 2 SELECT queries (before/after)
        - 1 UPDATE query (actual update)
        - 1 bulk_update (if hooks modify data)

        Trade-off: Hooks require loading data into Python. If you need
        maximum performance and don't need hooks, use bypass_hooks=True.

        Args:
            update_kwargs: Dict of fields to update
            bypass_hooks: Skip all hooks if True

        Returns:
            Number of rows updated
        """
        try:
            if bypass_hooks or get_bypass_hooks():
                return QuerySet.update(self.queryset, **update_kwargs)

            return self._execute_queryset_update_with_hooks(update_kwargs)
        finally:
            # CRITICAL: Return database connection to pool immediately
            # Prevents connection leaks in Celery tasks and long-running processes
            self._close_connection()

    @transaction.atomic
    def delete(self, bypass_hooks: bool = False) -> Tuple[int, Dict[str, int]]:
        """
        Execute delete with hooks.

        Args:
            bypass_hooks: Skip all hooks if True

        Returns:
            Tuple of (count, details dict)
        """
        try:
            objs = list(self.queryset)
            if not objs:
                return (0, {})

            self.analyzer.validate_for_delete(objs)

            changeset = build_changeset_for_delete(self.model_cls, objs)

            def operation():
                return QuerySet.delete(self.queryset)

            return self._execute_with_hooks(
                changeset=changeset,
                operation=operation,
                event_prefix="delete",
                bypass_hooks=bypass_hooks,
            )
        finally:
            # CRITICAL: Return database connection to pool immediately
            # Prevents connection leaks in Celery tasks and long-running processes
            self._close_connection()

    def clean(self, objs: List[Model], is_create: Optional[bool] = None) -> None:
        """
        Execute validation hooks only (no database operations).

        This is used by Django's clean() method to hook VALIDATE_* events
        without performing the actual operation.

        Args:
            objs: List of model instances to validate
            is_create: True for create, False for update, None to auto-detect
        """
        if not objs:
            return

        # Auto-detect operation type
        if is_create is None:
            is_create = objs[0].pk is None

        # Validate based on operation type
        if is_create:
            self.analyzer.validate_for_create(objs)
            changeset = build_changeset_for_create(self.model_cls, objs)
            event = "validate_create"
        else:
            self.analyzer.validate_for_update(objs)
            changeset = build_changeset_for_update(self.model_cls, objs, {})
            event = "validate_update"

        # Dispatch validation event
        model_classes = self.model_classes
        self._dispatch_hooks_for_models(model_classes, changeset, event)

    # ==================== QUERYSET UPDATE IMPLEMENTATION ====================

    def _execute_queryset_update_with_hooks(
        self,
        update_kwargs: Dict[str, Any],
    ) -> int:
        """
        Execute queryset update with full hook lifecycle support.

        Implements the fetch-update-fetch pattern required to support hooks
        with queryset.update(). BEFORE_UPDATE hooks can modify instances
        and modifications are auto-persisted.

        Optimized: Relationships are cached from old_instances and reattached
        to new_instances, avoiding a second SELECT with joins.

        Args:
            update_kwargs: Dict of fields to update

        Returns:
            Number of rows updated
        """
        # Step 1: Fetch old state with relationships preloaded
        logger.debug(f"🔴 QUERYSET_UPDATE: Fetching OLD instances BEFORE database update")
        hook_relationships = self._extract_hook_relationships()
        old_instances = self._fetch_instances_with_relationships(self.queryset, hook_relationships)

        if not old_instances:
            return 0

        old_records_map = {inst.pk: inst for inst in old_instances}

        # DEBUG: Log old record values
        for inst in old_instances:
            logger.debug(f"🔴 QUERYSET_UPDATE OLD: {inst.__class__.__name__} pk={inst.pk}")
            for key, value in update_kwargs.items():
                field_id = f"{key}_id" if not key.endswith("_id") else key
                if hasattr(inst, field_id):
                    old_value = inst.__dict__.get(field_id)
                    logger.debug(f"🔴 QUERYSET_UPDATE OLD: {field_id}={old_value} (before DB update)")

        # OPTIMIZATION: Cache relationship objects from old_instances for reuse
        cached_relationships = {}
        if hook_relationships:
            cached_relationships = self._cache_relationship_objects(old_instances, hook_relationships)
            logger.info(f"QUERYSET_UPDATE OPTIMIZATION: Cached {len(cached_relationships)} relationship sets for reuse")

        # Step 2: Execute native Django update
        logger.debug(f"🟠 QUERYSET_UPDATE: Executing database UPDATE with kwargs: {update_kwargs}")
        update_count = QuerySet.update(self.queryset, **update_kwargs)
        logger.debug(f"🟠 QUERYSET_UPDATE: Database UPDATE completed, {update_count} rows updated")
        if update_count == 0:
            return 0

        # Step 3: Fetch new state after update (WITHOUT expensive relationship joins)
        pks = extract_pks(old_instances)
        new_queryset = self.model_cls.objects.filter(pk__in=pks)
        logger.debug(f"🟡 QUERYSET_UPDATE: Fetching NEW instances AFTER database update")

        # OPTIMIZATION: Fetch without relationships first (faster)
        if hook_relationships and cached_relationships:
            logger.info("QUERYSET_UPDATE OPTIMIZATION: Fetching updated records without joins")
            new_instances = list(new_queryset)

            # DEBUG: Log new record values BEFORE reattaching relationships
            for inst in new_instances:
                logger.debug(f"🟡 QUERYSET_UPDATE NEW (before reattach): {inst.__class__.__name__} pk={inst.pk}")
                for key, value in update_kwargs.items():
                    field_id = f"{key}_id" if not key.endswith("_id") else key
                    if hasattr(inst, field_id):
                        new_value = inst.__dict__.get(field_id)
                        logger.debug(f"🟡 QUERYSET_UPDATE NEW (before reattach): {field_id}={new_value} (fresh from DB)")

            # Reattach cached relationships (but skip ones that were just updated)
            self._reattach_cached_relationships(new_instances, cached_relationships, hook_relationships, update_kwargs=update_kwargs)

            # DEBUG: Log new record values AFTER reattaching relationships
            for inst in new_instances:
                logger.debug(f"🟢 QUERYSET_UPDATE NEW (after reattach): {inst.__class__.__name__} pk={inst.pk}")
                for key, value in update_kwargs.items():
                    field_id = f"{key}_id" if not key.endswith("_id") else key
                    if hasattr(inst, field_id):
                        new_value = inst.__dict__.get(field_id)
                        logger.debug(f"🟢 QUERYSET_UPDATE NEW (after reattach): {field_id}={new_value} (after reattach)")
        else:
            # Fallback to original behavior if no relationships to cache
            new_instances = self._fetch_instances_with_relationships(new_queryset, hook_relationships)

        # Step 4: Build changeset and run hook lifecycle
        changeset = build_changeset_for_update(
            self.model_cls,
            new_instances,
            update_kwargs,
            old_records_map=old_records_map,
        )
        changeset.operation_meta["is_queryset_update"] = True
        changeset.operation_meta["allows_modifications"] = True

        model_classes = self.model_classes

        # Step 5: VALIDATE phase
        self._dispatch_hooks_for_models(model_classes, changeset, "validate_update", bypass_hooks=False)

        # Step 6: BEFORE_UPDATE phase with modification tracking
        modified_fields = self._run_before_update_hooks_with_tracking(new_instances, model_classes, changeset)

        # Step 7: Auto-persist BEFORE_UPDATE modifications
        if modified_fields:
            self._persist_hook_modifications(new_instances, modified_fields)

        # Step 8: AFTER_UPDATE phase (read-only)
        pre_after_state = self._snapshot_instance_state(new_instances)
        self._dispatch_hooks_for_models(model_classes, changeset, "after_update", bypass_hooks=False)

        # Step 9: Auto-persist any AFTER_UPDATE modifications (should be rare)
        after_modified_fields = self._detect_modifications(new_instances, pre_after_state)
        if after_modified_fields:
            logger.warning("AFTER_UPDATE hooks modified fields: %s. Consider moving modifications to BEFORE_UPDATE.", after_modified_fields)
            self._persist_hook_modifications(new_instances, after_modified_fields)

        return update_count

    def _run_before_update_hooks_with_tracking(self, instances: List[Model], model_classes: List[type], changeset: ChangeSet) -> Set[str]:
        """
        Run BEFORE_UPDATE hooks and detect modifications.

        Returns:
            Set of field names that were modified by hooks
        """
        pre_hook_state = self._snapshot_instance_state(instances)
        self._dispatch_hooks_for_models(model_classes, changeset, "before_update", bypass_hooks=False)
        return self._detect_modifications(instances, pre_hook_state)

    # ==================== HOOK ORCHESTRATION ====================

    def _execute_with_hooks(
        self,
        changeset: ChangeSet,
        operation: Callable,
        event_prefix: str,
        bypass_hooks: bool = False,
    ) -> Any:
        """
        Execute operation with hooks for the model.

        Args:
            changeset: ChangeSet for the model
            operation: Callable that performs the actual DB operation
            event_prefix: 'create', 'update', or 'delete'
            bypass_hooks: Skip all hooks if True

        Returns:
            Result of operation
        """
        if bypass_hooks:
            return operation()

        self.dispatcher._reset_executed_hooks()
        logger.debug("Starting %s operation for %s", event_prefix, changeset.model_cls.__name__)

        model_classes = self.model_classes

        # Preload relationships needed by hook conditions (prevents N+1)
        self._preload_condition_relationships_for_operation(changeset, model_classes)

        # VALIDATE phase
        self._dispatch_hooks_for_models(model_classes, changeset, f"validate_{event_prefix}")

        # BEFORE phase
        self._dispatch_hooks_for_models(model_classes, changeset, f"before_{event_prefix}")

        # Execute operation
        result = operation()

        # AFTER phase (handle upsert splitting for create operations)
        if result and isinstance(result, list) and event_prefix == "create":
            if self._is_upsert_operation(result):
                self._dispatch_upsert_after_hooks(result, model_classes)
            else:
                after_changeset = build_changeset_for_create(changeset.model_cls, result)
                self._dispatch_hooks_for_models(model_classes, after_changeset, f"after_{event_prefix}")
        else:
            self._dispatch_hooks_for_models(model_classes, changeset, f"after_{event_prefix}")

        return result

    def _dispatch_hooks_for_models(
        self,
        model_classes: List[type],
        changeset: ChangeSet,
        event_suffix: str,
        bypass_hooks: bool = False,
    ) -> None:
        """
        Dispatch hooks for model classes.

        Args:
            model_classes: List of model classes
            changeset: The changeset to use as base
            event_suffix: Event name suffix (e.g., 'before_create')
            bypass_hooks: Whether to skip hook execution
        """
        logger.debug("Dispatching %s to %d models: %s", event_suffix, len(model_classes), [m.__name__ for m in model_classes])

        for model_cls in model_classes:
            model_changeset = self._build_changeset_for_model(changeset, model_cls)
            self.dispatcher.dispatch(model_changeset, event_suffix, bypass_hooks=bypass_hooks)

    def _build_changeset_for_model(self, original_changeset: ChangeSet, target_model_cls: type) -> ChangeSet:
        """
        Build a changeset for a specific model class.

        This allows hooks to receive the same instances but with
        the correct model_cls for hook registration matching.

        Args:
            original_changeset: The original changeset
            target_model_cls: The model class to build changeset for

        Returns:
            ChangeSet for the target model
        """
        return ChangeSet(
            model_cls=target_model_cls,
            changes=original_changeset.changes,
            operation_type=original_changeset.operation_type,
            operation_meta=original_changeset.operation_meta,
        )

    # ==================== UPSERT HANDLING ====================

    def _classify_upsert_records(
        self,
        objs: List[Model],
        update_conflicts: bool,
        unique_fields: Optional[List[str]],
    ) -> Tuple[Set[Any], Dict[Any, Any]]:
        """
        Classify records for upsert operations.

        Args:
            objs: List of model instances
            update_conflicts: Whether this is an upsert operation
            unique_fields: Fields to check for conflicts

        Returns:
            Tuple of (existing_record_ids, existing_pks_map)
        """
        if not (update_conflicts and unique_fields):
            return set(), {}

        existing_ids, existing_pks = self.record_classifier.classify_for_upsert(objs, unique_fields)

        logger.info("Upsert classification: %d existing, %d new records", len(existing_ids), len(objs) - len(existing_ids))

        return existing_ids, existing_pks

    def _is_upsert_operation(self, result_objects: List[Model]) -> bool:
        """Check if the operation was an upsert (with update_conflicts=True)."""
        if not result_objects:
            return False
        return hasattr(result_objects[0], "_bulk_hooks_upsert_metadata")

    def _dispatch_upsert_after_hooks(self, result_objects: List[Model], model_classes: List[type]) -> None:
        """
        Dispatch after hooks for upsert operations, splitting by create/update.

        This matches Salesforce behavior where created records fire after_create
        and updated records fire after_update hooks.

        Args:
            result_objects: List of objects returned from the operation
            model_classes: List of model classes
        """
        created, updated = self._classify_upsert_results(result_objects)

        logger.info("Upsert after hooks: %d created, %d updated", len(created), len(updated))

        if created:
            create_changeset = build_changeset_for_create(self.model_cls, created)
            create_changeset.operation_meta["relationships_preloaded"] = True
            self._dispatch_hooks_for_models(model_classes, create_changeset, "after_create", bypass_hooks=False)

        if updated:
            # Use cached old records (fetched BEFORE operation) for proper change detection
            old_records_map = self._upsert_old_records_map or {}
            update_changeset = build_changeset_for_update(self.model_cls, updated, {}, old_records_map=old_records_map)
            update_changeset.operation_meta["relationships_preloaded"] = True
            self._dispatch_hooks_for_models(model_classes, update_changeset, "after_update", bypass_hooks=False)

        self._cleanup_upsert_metadata(result_objects)

        # Clear the cached old records
        self._upsert_old_records_map = None

    def _classify_upsert_results(self, result_objects: List[Model]) -> Tuple[List[Model], List[Model]]:
        """
        Classify upsert results into created and updated objects.

        Returns:
            Tuple of (created_objects, updated_objects)
        """
        created_objects = []
        updated_objects = []
        objects_needing_timestamp_check = []

        # First pass: collect objects with metadata
        for obj in result_objects:
            if hasattr(obj, "_bulk_hooks_was_created"):
                if obj._bulk_hooks_was_created:
                    created_objects.append(obj)
                else:
                    updated_objects.append(obj)
            else:
                objects_needing_timestamp_check.append(obj)

        # Second pass: bulk check timestamps for objects without metadata
        if objects_needing_timestamp_check:
            created, updated = self._classify_by_timestamps(objects_needing_timestamp_check)
            created_objects.extend(created)
            updated_objects.extend(updated)

        return created_objects, updated_objects

    def _classify_by_timestamps(self, objects: List[Model]) -> Tuple[List[Model], List[Model]]:
        """
        Classify objects as created or updated based on timestamp comparison.

        Returns:
            Tuple of (created_objects, updated_objects)
        """
        created = []
        updated = []

        # Group by model class
        objects_by_model = {}
        for obj in objects:
            model_cls = obj.__class__
            objects_by_model.setdefault(model_cls, []).append(obj)

        # Process each model class
        for model_cls, objs in objects_by_model.items():
            if not (hasattr(model_cls, "created_at") and hasattr(model_cls, "updated_at")):
                # No timestamp fields, default to created
                created.extend(objs)
                continue

            # Bulk fetch timestamps
            pks = extract_pks(objs)
            if not pks:
                created.extend(objs)
                continue

            timestamp_map = {
                record["pk"]: (record["created_at"], record["updated_at"])
                for record in model_cls.objects.filter(pk__in=pks).values("pk", "created_at", "updated_at")
            }

            # Classify based on timestamp difference
            for obj in objs:
                if obj.pk not in timestamp_map:
                    created.append(obj)
                    continue

                created_at, updated_at = timestamp_map[obj.pk]
                if not (created_at and updated_at):
                    created.append(obj)
                    continue

                time_diff = abs((updated_at - created_at).total_seconds())
                if time_diff <= self.UPSERT_TIMESTAMP_THRESHOLD_SECONDS:
                    created.append(obj)
                else:
                    updated.append(obj)

        return created, updated

    def _cleanup_upsert_metadata(self, result_objects: List[Model]) -> None:
        """Clean up temporary metadata added during upsert operations."""
        for obj in result_objects:
            for attr in ("_bulk_hooks_was_created", "_bulk_hooks_upsert_metadata"):
                if hasattr(obj, attr):
                    delattr(obj, attr)

    # ==================== INSTANCE STATE TRACKING ====================

    def _snapshot_instance_state(self, instances: List[Model]) -> Dict[Any, Dict[str, Any]]:
        """
        Create a snapshot of current instance field values.

        Args:
            instances: List of model instances

        Returns:
            Dict mapping pk -> {field_name: value}
        """
        snapshot = {}

        for instance in instances:
            if instance.pk is None:
                continue

            field_values = {}
            for field in self.model_cls._meta.get_fields():
                # Skip non-concrete fields
                if field.many_to_many or field.one_to_many:
                    continue

                try:
                    field_values[field.name] = getattr(instance, field.name)
                except (AttributeError, FieldDoesNotExist):
                    field_values[field.name] = None

            snapshot[instance.pk] = field_values

        return snapshot

    def _detect_modifications(
        self,
        instances: List[Model],
        pre_hook_state: Dict[Any, Dict[str, Any]],
    ) -> Set[str]:
        """
        Detect which fields were modified by comparing to snapshot.

        Args:
            instances: List of model instances
            pre_hook_state: Previous state snapshot

        Returns:
            Set of field names that were modified
        """
        modified_fields = set()

        for instance in instances:
            if instance.pk not in pre_hook_state:
                continue

            old_values = pre_hook_state[instance.pk]

            for field_name, old_value in old_values.items():
                try:
                    current_value = getattr(instance, field_name)
                except (AttributeError, FieldDoesNotExist):
                    current_value = None

                if current_value != old_value:
                    modified_fields.add(field_name)

        return modified_fields

    def _persist_hook_modifications(self, instances: List[Model], modified_fields: Set[str]) -> None:
        """
        Persist modifications made by hooks using bulk_update.

        Args:
            instances: List of modified instances
            modified_fields: Set of field names that were modified
        """
        logger.info("Hooks modified %d field(s): %s", len(modified_fields), ", ".join(sorted(modified_fields)))
        logger.info("Auto-persisting modifications via bulk_update")

        # Use Django's bulk_update directly (not our hook version)
        fresh_qs = QuerySet(model=self.model_cls, using=self.queryset.db)
        QuerySet.bulk_update(fresh_qs, instances, list(modified_fields))

    # ==================== RELATIONSHIP PRELOADING ====================

    def _fetch_instances_with_relationships(
        self,
        queryset: QuerySet,
        relationships: Set[str],
    ) -> List[Model]:
        """
        Fetch instances with relationships preloaded.

        Args:
            queryset: QuerySet to fetch from
            relationships: Set of relationship names to preload

        Returns:
            List of model instances with relationships loaded
        """
        if relationships:
            logger.info("Fetching instances with select_related(%s)", list(relationships))
            queryset = queryset.select_related(*relationships)
        else:
            logger.info("Fetching instances without select_related")

        return list(queryset)

    def _cache_relationship_objects(
        self,
        instances: List[Model],
        relationships: Set[str],
    ) -> Dict[Any, Dict[str, Any]]:
        """
        Cache relationship objects from instances for later reuse.

        This optimization allows us to avoid re-fetching relationships that
        haven't changed (common in queryset.update() operations).

        Args:
            instances: List of model instances with relationships loaded
            relationships: Set of relationship field names to cache

        Returns:
            Dict mapping pk -> {relationship_name: related_object}
        """
        cached = {}

        for instance in instances:
            if instance.pk is None:
                continue

            instance_cache = {}
            for rel_name in relationships:
                try:
                    # Get the related object (might be None)
                    related_obj = getattr(instance, rel_name, None)
                    instance_cache[rel_name] = related_obj
                except Exception as e:
                    logger.debug(f"Could not cache relationship '{rel_name}': {e}")
                    instance_cache[rel_name] = None

            cached[instance.pk] = instance_cache

        return cached

    def _reattach_cached_relationships(
        self,
        instances: List[Model],
        cached_relationships: Dict[Any, Dict[str, Any]],
        relationships: Set[str],
        update_kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Reattach cached relationship objects to instances.

        This avoids re-querying the database for relationships that haven't
        changed during the update operation.

        CRITICAL: Does not reattach relationships for FK fields that were
        just updated in the queryset.update() operation.

        Args:
            instances: List of model instances to attach relationships to
            cached_relationships: Cached relationship objects from before update
            relationships: Set of relationship field names to reattach
            update_kwargs: Dict of fields that were updated (to skip reattaching)
        """
        logger.debug(f"🟣 REATTACH: Called with {len(instances)} instances and relationships: {relationships}")

        # Determine which FK fields were updated and should NOT be reattached
        skip_relationships = set()
        if update_kwargs:
            for key in update_kwargs.keys():
                # If updating business_id, don't reattach 'business'
                # If updating business, don't reattach 'business'
                if key.endswith("_id"):
                    rel_name = key[:-3]  # Remove '_id' suffix
                    skip_relationships.add(rel_name)
                else:
                    skip_relationships.add(key)

            if skip_relationships:
                logger.debug(f"🟣 REATTACH: Will skip these relationships that were updated: {skip_relationships}")

        for instance in instances:
            if instance.pk is None:
                continue

            cached = cached_relationships.get(instance.pk)
            if not cached:
                continue

            for rel_name in relationships:
                # CRITICAL FIX: Don't reattach relationships for fields that were just updated
                if rel_name in skip_relationships:
                    logger.debug(f"🟣 REATTACH: Skipping '{rel_name}' because it was just updated")
                    continue

                if rel_name in cached:
                    try:
                        # DEBUG: Check FK value BEFORE reattaching
                        fk_field_name = f"{rel_name}_id"
                        fk_value_before = instance.__dict__.get(fk_field_name) if hasattr(instance, fk_field_name) else None

                        # Reattach the cached related object
                        related_obj = cached[rel_name]
                        setattr(instance, rel_name, related_obj)

                        # Also set the FK _id field if the relationship has one
                        if related_obj is not None and hasattr(instance, fk_field_name):
                            fk_value_after = related_obj.pk

                            # DEBUG: Log if we're overwriting a changed FK value
                            if fk_value_before != fk_value_after:
                                logger.warning(
                                    f"🚨 REATTACH_BUG: Overwriting {instance.__class__.__name__}.{fk_field_name} "
                                    f"from {fk_value_before} to {fk_value_after} for pk={instance.pk}"
                                )

                            setattr(instance, fk_field_name, related_obj.pk)
                    except Exception as e:
                        logger.debug(f"Could not reattach relationship '{rel_name}': {e}")

    def _preload_condition_relationships_for_operation(
        self,
        changeset: ChangeSet,
        model_classes: List[type],
    ) -> None:
        """
        Preload relationships needed by hook conditions for this operation.

        This prevents N+1 queries by loading all necessary relationships upfront.

        Args:
            changeset: The changeset for this operation
            model_classes: List of model classes
        """
        relationships = self._extract_condition_relationships_for_operation(changeset, model_classes)

        if relationships:
            logger.info("Bulk preloading %d condition relationships for %s hooks", len(relationships), changeset.model_cls.__name__)
            self.dispatcher.preload_relationships(changeset, relationships)
            changeset.operation_meta["relationships_preloaded"] = True
        else:
            logger.info("No condition relationships to preload for %s hooks", changeset.model_cls.__name__)

    def _extract_condition_relationships_for_operation(
        self,
        changeset: ChangeSet,
        model_classes: List[type],
    ) -> Set[str]:
        """
        Extract relationships needed by hook conditions for this operation.

        Args:
            changeset: The changeset for this operation
            model_classes: List of model classes

        Returns:
            Set of relationship field names to preload
        """
        relationships = set()
        event_prefix = changeset.operation_type
        events_to_check = [f"validate_{event_prefix}", f"before_{event_prefix}", f"after_{event_prefix}"]

        for model_cls in model_classes:
            for event in events_to_check:
                hooks = self.dispatcher.registry.get_hooks(model_cls, event)

                for handler_cls, method_name, condition, priority in hooks:
                    if condition:
                        condition_rels = self.dispatcher._extract_condition_relationships(condition, model_cls)
                        relationships.update(condition_rels)

        return relationships

    def _extract_hook_relationships(self) -> Set[str]:
        """
        Extract all relationship paths that hooks might access.

        This includes both condition relationships and @select_related decorators
        for the model. Prevents N+1 queries during bulk operations.

        Returns:
            Set of relationship field names to preload with select_related
        """
        relationships = set()
        models_to_check = self.model_classes
        events_to_check = ["before_update", "after_update", "validate_update"]

        for model_cls in models_to_check:
            logger.info("Checking hooks for model %s", model_cls.__name__)

            for event in events_to_check:
                hooks = self.dispatcher.registry.get_hooks(model_cls, event)
                logger.info("Found %d hooks for %s.%s", len(hooks), model_cls.__name__, event)

                for handler_cls, method_name, condition, priority in hooks:
                    # Extract from conditions
                    if condition:
                        condition_rels = self.dispatcher._extract_condition_relationships(condition, model_cls)
                        if condition_rels:
                            logger.info("Condition relationships for %s.%s: %s", model_cls.__name__, method_name, condition_rels)
                            relationships.update(condition_rels)

                    # Extract from @select_related decorators
                    try:
                        method = getattr(handler_cls, method_name, None)
                        if method:
                            select_related_fields = getattr(method, "_select_related_fields", None)
                            if select_related_fields and hasattr(select_related_fields, "__iter__"):
                                logger.info(
                                    "@select_related fields on %s.%s: %s", handler_cls.__name__, method_name, list(select_related_fields)
                                )
                                relationships.update(select_related_fields)
                    except Exception as e:
                        logger.warning("Failed to extract @select_related from %s.%s: %s", handler_cls.__name__, method_name, e)

        # Also preload all forward FK relationships on the model (aggressive approach)
        try:
            for field in self.model_cls._meta.get_fields():
                if field.is_relation and not field.many_to_many and not field.one_to_many:
                    relationships.add(field.name)
                    logger.info("AUTO: Adding FK relationship field %s", field.name)
        except Exception as e:
            logger.warning("Failed to extract all relationship fields: %s", e)

        logger.info("Total extracted relationships for %s: %s", self.model_cls.__name__, list(relationships))

        return relationships

    # ==================== HELPER METHODS ====================

    def _build_update_changeset(
        self,
        objs: List[Model],
        fields: List[str],
        old_records_map: Dict[Any, Model],
    ) -> ChangeSet:
        """
        Build a changeset for bulk update operations.

        Args:
            objs: List of model instances to update
            fields: List of field names to update
            old_records_map: Map of pk -> old record

        Returns:
            ChangeSet for the update operation
        """
        changes = [
            RecordChange(
                new_record=obj,
                old_record=old_records_map.get(obj.pk),
                changed_fields=fields,
            )
            for obj in objs
        ]

        return ChangeSet(self.model_cls, changes, "update", {"fields": fields})
