import logging
from functools import lru_cache
from typing import Any
from typing import List
from typing import Set

logger = logging.getLogger(__name__)


class RelationshipPreloader:
    """Handles efficient relationship preloading to prevent N+1 queries."""

    def __init__(self, model_cls):
        self.model_cls = model_cls

    def preload_for_records(
        self,
        records: List[Any],
        relationships: Set[str],
        preserve_fk_values: bool = True,
    ) -> None:
        """
        Preload relationships for a list of records.

        Args:
            records: List of model instances
            relationships: Set of relationship field names
            preserve_fk_values: Whether to preserve FK _id values after setattr
        """
        if not records or not relationships:
            return

        saved_records = [r for r in records if r.pk is not None]
        unsaved_records = [r for r in records if r.pk is None]

        if saved_records:
            self._preload_saved_records(saved_records, relationships, preserve_fk_values)

        if unsaved_records:
            self._preload_unsaved_records(unsaved_records, relationships, preserve_fk_values)

    def _preload_saved_records(
        self,
        records: List[Any],
        relationships: Set[str],
        preserve_fk_values: bool,
    ) -> None:
        """Preload relationships for saved records using select_related."""

        pks = [r.pk for r in records]

        logger.info(
            "SAVED RECORDS PRELOAD: %s records, relationships=%s",
            len(records),
            list(relationships),
        )

        preloaded = self.model_cls.objects.filter(pk__in=pks).select_related(*relationships).in_bulk()

        for record in records:
            if record.pk not in preloaded:
                continue

            preloaded_record = preloaded[record.pk]
            self._attach_relationships(
                record,
                preloaded_record,
                relationships,
                preserve_fk_values,
            )

    def _preload_unsaved_records(
        self,
        records: List[Any],
        relationships: Set[str],
        preserve_fk_values: bool,
    ) -> None:
        """Preload relationships for unsaved records by bulk-loading FK targets."""
        logger.info("UNSAVED RECORDS PRELOAD: %s records, relationships=%s", len(records), list(relationships))

        # Collect FK IDs for each relationship
        field_ids_map = {rel: set() for rel in relationships}

        for record in records:
            for rel in relationships:
                fk_id = getattr(record, f"{rel}_id", None)
                if fk_id is not None:
                    field_ids_map[rel].add(fk_id)
                    logger.debug("UNSAVED RECORD: %s has %s_id=%s", record, rel, fk_id)

        # Bulk load related objects
        field_objects_map = self._bulk_load_related_objects(field_ids_map)

        # Attach relationships
        for record in records:
            for rel in relationships:
                fk_id = getattr(record, f"{rel}_id", None)
                if fk_id and rel in field_objects_map:
                    related_obj = field_objects_map[rel].get(fk_id)
                    if related_obj:
                        logger.debug("ATTACHING: %s.%s = %s", record, rel, related_obj)
                        self._attach_single_relationship(
                            record,
                            rel,
                            related_obj,
                            preserve_fk_values,
                        )
                    else:
                        logger.warning("NO RELATED OBJECT: %s_id=%s not found in %s", rel, fk_id, rel)

    def _bulk_load_related_objects(
        self,
        field_ids_map: dict[str, Set[Any]],
    ) -> dict[str, dict[Any, Any]]:
        """Bulk load related objects for multiple fields."""

        field_objects_map = {}

        for field, ids in field_ids_map.items():
            if not ids:
                continue

            try:
                related_model = self._get_related_model(field)
                if related_model:
                    # Regular in_bulk loading
                    logger.debug("BULK LOAD: Loading %s %s objects", len(ids), related_model.__name__)
                    field_objects_map[field] = related_model.objects.in_bulk(ids)

                    logger.info(f"Preloaded {len(field_objects_map[field])} {related_model.__name__} objects for '{field}'")
            except Exception as e:
                logger.warning(f"Failed to preload field '{field}': {e}")
                field_objects_map[field] = {}

        return field_objects_map

    def _attach_relationships(
        self,
        target_record: Any,
        source_record: Any,
        relationships: Set[str],
        preserve_fk_values: bool,
    ) -> None:
        """Attach relationships from source to target record."""
        for rel in relationships:
            if hasattr(source_record, rel):
                related_obj = getattr(source_record, rel)
                self._attach_single_relationship(
                    target_record,
                    rel,
                    related_obj,
                    preserve_fk_values,
                )

    def _attach_single_relationship(
        self,
        record: Any,
        field_name: str,
        related_obj: Any,
        preserve_fk_values: bool,
    ) -> None:
        """Attach a single relationship while optionally preserving FK values."""
        fk_field_name = f"{field_name}_id"

        # Preserve FK value if requested and it was explicitly set
        preserved_fk = None
        should_restore = False

        if preserve_fk_values and fk_field_name in record.__dict__:
            preserved_fk = record.__dict__[fk_field_name]
            should_restore = True

        # Set the relationship
        setattr(record, field_name, related_obj)

        # Restore FK value if needed
        if should_restore:
            record.__dict__[fk_field_name] = preserved_fk

            # Clear cache if FK is None to prevent stale relationship access
            if preserved_fk is None and hasattr(record, "_state"):
                if hasattr(record._state, "fields_cache"):
                    record._state.fields_cache.pop(field_name, None)

    @lru_cache(maxsize=128)
    def _get_related_model(self, field_name: str):
        """Get the related model for a field (cached)."""
        from django_bulk_hooks.operations.field_utils import _get_field_or_none

        field = _get_field_or_none(self.model_cls, field_name)
        if field and field.is_relation and hasattr(field, "remote_field"):
            return field.remote_field.model
        return None

    @lru_cache(maxsize=128)
    def is_relationship_field(self, field_name: str) -> bool:
        """Check if a field is a relationship field (cached)."""
        from django_bulk_hooks.operations.field_utils import _get_field_or_none

        field = _get_field_or_none(self.model_cls, field_name)
        return field is not None and field.is_relation and not field.many_to_many
