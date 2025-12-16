"""
Helper functions for building ChangeSets from operation contexts.

These functions eliminate duplication across queryset.py, bulk_operations.py,
and models.py by providing reusable ChangeSet builders.

NOTE: These helpers are pure changeset builders - they don't fetch data.
Data fetching is the responsibility of ModelAnalyzer.
"""

import logging
from functools import lru_cache

from django_bulk_hooks.changeset import ChangeSet
from django_bulk_hooks.changeset import RecordChange

logger = logging.getLogger(__name__)


def extract_pks(objects):
    """
    Extract non-None primary keys from objects.

    Args:
        objects: Iterable of model instances or objects with pk attribute

    Returns:
        List of non-None primary key values
    """
    return [obj.pk for obj in objects if obj.pk is not None]


def build_changeset_for_update(
    model_cls,
    instances,
    update_kwargs,
    old_records_map=None,
    **meta,
):
    """
    Build ChangeSet for update operations.

    Args:
        model_cls: Django model class
        instances: List of instances being updated
        update_kwargs: Dict of fields being updated
        old_records_map: Optional dict of {pk: old_instance}. If None, no old records.
        **meta: Additional metadata (e.g., has_subquery=True, lock_records=False)

    Returns:
        ChangeSet instance ready for dispatcher
    """
    if old_records_map is None:
        old_records_map = {}

    # Smart pre-computation logic:
    # - If update_kwargs non-empty and old_records exist: Don't precompute (QuerySet.update case)
    # - If update_kwargs empty and old_records exist: Don't precompute (upsert case)
    # - If update_kwargs empty and no old_records: Precompute as empty (validation case)
    should_precompute = not bool(update_kwargs) and old_records_map is None
    changed_fields = list(update_kwargs.keys()) if should_precompute else None

    changes = [
        RecordChange(
            new,
            old_records_map.get(new.pk),
            changed_fields=changed_fields,
        )
        for new in instances
    ]

    operation_meta = {"update_kwargs": update_kwargs}
    operation_meta.update(meta)

    return ChangeSet(model_cls, changes, "update", operation_meta)


def build_changeset_for_create(model_cls, instances, **meta):
    """
    Build ChangeSet for create operations.

    Args:
        model_cls: Django model class
        instances: List of instances being created
        **meta: Additional metadata (e.g., batch_size=1000)

    Returns:
        ChangeSet instance ready for dispatcher
    """
    changes = [RecordChange(new, None) for new in instances]
    return ChangeSet(model_cls, changes, "create", meta)


def build_changeset_for_delete(model_cls, instances, **meta):
    """
    Build ChangeSet for delete operations.

    For delete, the "new_record" is the object being deleted (current state),
    and old_record is also the same (or None). This matches Salesforce behavior
    where Hook.new contains the records being deleted.

    Args:
        model_cls: Django model class
        instances: List of instances being deleted
        **meta: Additional metadata

    Returns:
        ChangeSet instance ready for dispatcher
    """
    changes = [
        RecordChange(obj, obj)  # new_record and old_record are the same for delete
        for obj in instances
    ]
    return ChangeSet(model_cls, changes, "delete", meta)


@lru_cache(maxsize=256)
def _get_model_fields_map(model_cls, include_relations=False):
    """
    Get a cached mapping of field names to field objects for a model.

    Cached for performance - repeated calls for the same model are O(1).

    Args:
        model_cls: Django model class
        include_relations: Whether to include relation fields

    Returns:
        Frozen dictionary mapping field names to field objects
    """
    fields_by_name = {}
    # Use local_fields for child tables, get_fields() for parent tables that need inherited fields
    fields_to_check = model_cls._meta.local_fields if not include_relations else model_cls._meta.get_fields()
    for field in fields_to_check:
        if not include_relations and (field.many_to_many or field.one_to_many):
            continue
        fields_by_name[field.name] = field
    # Return a tuple of items so it's hashable for caching
    return tuple(fields_by_name.items())


def get_fields_for_model(model_cls, field_names, include_relations=False):
    """
    Get field objects for the given model from a list of field names.

    Handles field name normalization (e.g., 'field_id' -> 'field').
    Only returns fields that actually exist on the model.

    Args:
        model_cls: Django model class
        field_names: List of field names (strings)
        include_relations: Whether to include relation fields (default False)

    Returns:
        List of field objects that exist on the model, in the same order as field_names
    """
    if not field_names:
        return []

    # Get cached field mapping
    fields_items = _get_model_fields_map(model_cls, include_relations)
    fields_by_name = dict(fields_items)

    # Handle field name normalization and preserve order
    result = []
    seen = set()

    for name in field_names:
        # Try original name first
        if name in fields_by_name and name not in seen:
            result.append(fields_by_name[name])
            seen.add(name)
        # Try normalized name (field_id -> field)
        elif name.endswith("_id") and name[:-3] in fields_by_name and name[:-3] not in seen:
            result.append(fields_by_name[name[:-3]])
            seen.add(name[:-3])

    return result


@lru_cache(maxsize=256)
def _get_model_field_names(model_cls):
    """
    Get a cached set of field names for a model.

    Cached for performance - repeated calls for the same model are O(1).

    Args:
        model_cls: Django model class

    Returns:
        Frozen set of field names
    """
    return frozenset(field.name for field in model_cls._meta.local_fields)


def filter_field_names_for_model(model_cls, field_names):
    """
    Filter a list of field names to only those that exist on the model.

    Handles field name normalization (e.g., 'field_id' -> 'field').

    Args:
        model_cls: Django model class
        field_names: List of field names (strings)

    Returns:
        List of field names that exist on the model
    """
    if not field_names:
        return []

    # Get cached field names
    available_names = _get_model_field_names(model_cls)

    result = []
    for name in field_names:
        if name in available_names:
            result.append(name)
        elif name.endswith("_id") and name[:-3] in available_names:
            result.append(name[:-3])

    return result


def dispatch_hooks_for_operation(changeset, event, bypass_hooks=False, dispatcher=None):
    """
    Dispatch hooks for an operation.

    This function follows Salesforce's pattern of isolated per-operation context.
    When called from a coordinator, the dispatcher is provided (per-operation).
    When called directly (e.g., in tests or standalone scripts), a fresh
    dispatcher is created for that specific operation.

    Args:
        changeset: ChangeSet instance
        event: Event name (e.g., 'before_update', 'after_create')
        bypass_hooks: If True, skip hook execution
        dispatcher: Optional dispatcher instance. If None, creates a fresh one
                   for this operation (Salesforce per-transaction pattern).

    Note:
        Creating a fresh dispatcher per operation prevents memory leaks
        in long-lived processes by ensuring state is garbage collected
        after each operation completes.
    """
    if dispatcher is None:
        # Create fresh dispatcher for standalone usage
        from django_bulk_hooks.dispatcher import HookDispatcher
        from django_bulk_hooks.registry import get_registry

        dispatcher = HookDispatcher(get_registry())

    dispatcher.dispatch(changeset, event, bypass_hooks=bypass_hooks)


def tag_upsert_metadata(result_objects, existing_record_ids, existing_pks_map):
    """
    Tag objects with metadata indicating whether they were created or updated.

    Args:
        result_objects: List of objects returned from bulk operation
        existing_record_ids: Set of id() for objects that existed before
        existing_pks_map: Dict mapping id(obj) -> pk for existing records
    """
    existing_pks = set(existing_pks_map.values())

    created_count = 0
    updated_count = 0

    for obj in result_objects:
        # Use PK to determine if this record was created or updated
        was_created = obj.pk not in existing_pks
        obj._bulk_hooks_was_created = was_created
        obj._bulk_hooks_upsert_metadata = True

        if was_created:
            created_count += 1
        else:
            updated_count += 1

    logger.info(
        f"Tagged upsert metadata: {created_count} created, {updated_count} updated "
        f"(total={len(result_objects)}, existing_pks={len(existing_pks)})"
    )


def was_created(obj):
    """Check if an object was created in an upsert operation."""
    return getattr(obj, "_bulk_hooks_was_created", False)


def is_upsert_result(obj):
    """Check if an object has upsert metadata."""
    return getattr(obj, "_bulk_hooks_upsert_metadata", False)


def cleanup_upsert_metadata(objects):
    """
    Clean up upsert metadata after hook execution.

    Args:
        objects: Objects to clean up
    """
    for obj in objects:
        if hasattr(obj, "_bulk_hooks_was_created"):
            delattr(obj, "_bulk_hooks_was_created")
        if hasattr(obj, "_bulk_hooks_upsert_metadata"):
            delattr(obj, "_bulk_hooks_upsert_metadata")
