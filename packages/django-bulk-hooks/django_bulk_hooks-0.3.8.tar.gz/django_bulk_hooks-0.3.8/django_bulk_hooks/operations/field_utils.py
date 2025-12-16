"""
Field value extraction and normalization utilities.

Provides a single source of truth for converting Django model instance field values
to their database representation, with proper handling of foreign keys.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable

from django.db import models
from django.db.models import Field
from django.db.models import ForeignKey

if TYPE_CHECKING:
    from django.db.models import Model

logger = logging.getLogger(__name__)


class FieldValueError(Exception):
    """Raised when field value extraction fails."""


# ============================================================================
# Public API - Field Value Extraction
# ============================================================================


def get_field_value_for_db(
    obj: Model,
    field_name: str,
    model_cls: type[Model] | None = None,
) -> Any:
    """
    Extract a field value from a model instance in database-ready form.

    For regular fields: returns the field value as-is.
    For FK fields: returns the primary key (integer) instead of the related object.

    This ensures consistent handling across all operations (upsert classification,
    bulk create, bulk update, etc.).

    Args:
        obj: Model instance to extract value from
        field_name: Name of the field to extract
        model_cls: Model class (defaults to obj's class if not provided)

    Returns:
        Database-ready value (FK as integer, regular fields as-is)

    Example:
        >>> obj = Business(name="Acme", parent_id=5)
        >>> get_field_value_for_db(obj, "parent_id")
        5
        >>> get_field_value_for_db(obj, "name")
        'Acme'
    """
    model_cls = model_cls or obj.__class__

    logger.debug(
        "Extracting field '%s' from %s instance (pk=%s)",
        field_name,
        obj.__class__.__name__,
        getattr(obj, "pk", None),
    )

    field = _get_field_or_none(model_cls, field_name)

    if field is None:
        # Field doesn't exist in model definition - fall back to attribute access
        logger.debug(
            "Field '%s' not found in model metadata, using getattr fallback",
            field_name,
        )
        return getattr(obj, field_name, None)

    if isinstance(field, ForeignKey):
        return _extract_fk_value(obj, field_name, field, model_cls)

    return _extract_regular_value(obj, field_name, model_cls)


def get_field_values_for_db(
    obj: Model,
    field_names: Iterable[str],
    model_cls: type[Model] | None = None,
) -> dict[str, Any]:
    """
    Extract multiple field values from a model instance in database-ready form.

    Args:
        obj: Model instance
        field_names: Iterable of field names to extract
        model_cls: Model class (defaults to obj's class if not provided)

    Returns:
        Dictionary mapping field names to their database-ready values

    Example:
        >>> obj = Business(name="Acme", parent_id=5)
        >>> get_field_values_for_db(obj, ["name", "parent_id"])
        {'name': 'Acme', 'parent_id': 5}
    """
    model_cls = model_cls or obj.__class__
    return {field_name: get_field_value_for_db(obj, field_name, model_cls) for field_name in field_names}


# ============================================================================
# Field Comparison & Change Detection
# ============================================================================


def get_changed_fields(
    old_obj: Model,
    new_obj: Model,
    model_cls: type[Model],
    skip_auto_fields: bool = False,
) -> set[str]:
    """
    Identify fields that have changed between two model instances.

    Uses Django's field.get_prep_value() for proper database-level comparison,
    handling timezone conversions, type coercions, etc.

    Args:
        old_obj: The original model instance
        new_obj: The modified model instance
        model_cls: The Django model class
        skip_auto_fields: Whether to skip auto-created fields (default: False)

    Returns:
        Set of field names that have changed

    Example:
        >>> old = Business(name="Acme", status="active")
        >>> new = Business(name="Acme Corp", status="active")
        >>> get_changed_fields(old, new, Business)
        {'name'}
    """
    changed = set()

    for field in model_cls._meta.fields:
        if field.primary_key:
            continue

        if skip_auto_fields and field.auto_created:
            continue

        if _field_value_changed(field, old_obj, new_obj):
            changed.add(field.name)

    return changed


# ============================================================================
# Field Name Normalization
# ============================================================================


def normalize_field_name_to_db(field_name: str, model_cls: type[Model]) -> str:
    """
    Normalize a field name to its database column name.

    For FK fields referenced by relationship name, returns the attname
    (e.g., 'business' -> 'business_id').
    For regular fields, returns the name as-is.

    Args:
        field_name: Field name (can be relationship name like 'business' or column name like 'business_id')
        model_cls: Model class

    Returns:
        Database column name

    Example:
        >>> normalize_field_name_to_db("business", Location)
        'business_id'
        >>> normalize_field_name_to_db("name", Location)
        'name'
    """
    field = _get_field_or_none(model_cls, field_name)

    if field and isinstance(field, ForeignKey):
        return field.attname

    return field_name


# ============================================================================
# Auto Field Utilities
# ============================================================================


@lru_cache(maxsize=256)
def get_auto_fields(
    model_cls: type[Model],
    include_auto_now_add: bool = True,
) -> tuple[str, ...]:
    """
    Get auto-updating field names from a model.

    Cached for performance - repeated calls for the same model are O(1).

    Args:
        model_cls: Django model class
        include_auto_now_add: Whether to include auto_now_add fields (default: True)

    Returns:
        Tuple of auto field names (auto_now and optionally auto_now_add)

    Example:
        >>> get_auto_fields(Business)
        ('modified_at', 'created_at')
        >>> get_auto_fields(Business, include_auto_now_add=False)
        ('modified_at',)
    """
    fields = []
    for field in model_cls._meta.fields:
        if getattr(field, "auto_now", False):
            fields.append(field.name)
        elif include_auto_now_add and getattr(field, "auto_now_add", False):
            fields.append(field.name)

    return tuple(fields)


@lru_cache(maxsize=256)
def get_fk_fields(model_cls: type[Model]) -> tuple[str, ...]:
    """
    Get foreign key field names for a model.

    Cached for performance - repeated calls for the same model are O(1).

    Args:
        model_cls: Django model class

    Returns:
        Tuple of FK field names (relationship names, not column names)

    Example:
        >>> get_fk_fields(Location)
        ('business', 'parent')
    """
    return tuple(field.name for field in model_cls._meta.concrete_fields if field.is_relation and not field.many_to_many)


# ============================================================================
# Auto-now Utilities
# ============================================================================


def handle_auto_now_fields_for_models(
    models: Iterable[type[Model]],
    instances: Iterable[Model],
    for_update: bool = True,
) -> set[str]:
    """
    Handle auto-now fields across model classes.

    Pre-saves auto fields on instances and returns the set of field names
    that should be included in database operations.

    Args:
        models: Model classes
        instances: Model instances to process
        for_update: True for update operations, False for create operations

    Returns:
        Set of auto field names to include in the database operation

    Example:
        >>> # For an update operation
        >>> fields = handle_auto_now_fields_for_models(
        ...     [MyModel],
        ...     [instance1, instance2],
        ...     for_update=True
        ... )
        >>> # Returns {'modified_at'} and updates modified_at on instances
    """
    auto_fields = set()
    instances_list = list(instances)  # Ensure we can iterate multiple times

    for model_cls in models:
        for field in model_cls._meta.local_fields:
            should_include = _should_include_auto_field(field, for_update)

            if should_include:
                auto_fields.add(field.name)
                _pre_save_field_on_instances(field, instances_list, for_update)

    return auto_fields


def handle_auto_now_fields(
    model: type[Model],
    instances: Iterable[Model],
    for_update: bool = True,
) -> set[str]:
    """
    Handle auto-now fields for a single model.

    Pre-saves auto fields on instances and returns the set of field names
    that should be included in database operations.

    Args:
        model: Model class
        instances: Model instances to process
        for_update: True for update operations, False for create operations

    Returns:
        Set of auto field names to include in the database operation
    """
    return handle_auto_now_fields_for_models([model], instances, for_update=for_update)


# ============================================================================
# Private Helper Functions
# ============================================================================


@lru_cache(maxsize=512)
def _get_field_or_none(model_cls: type[Model], field_name: str) -> Field | None:
    """
    Get a field from model metadata, returning None if not found.

    Cached for performance - field lookups are O(1) after first access.
    """
    try:
        return model_cls._meta.get_field(field_name)
    except Exception:  # FieldDoesNotExist or other Django exceptions
        return None


def _extract_fk_value(
    obj: Model,
    field_name: str,
    field: ForeignKey,
    model_cls: type[Model],
) -> Any:
    """
    Extract the primary key value from a foreign key field.
    """
    attname = field.attname
    was_explicitly_set = attname in obj.__dict__

    logger.debug(
        "Extracting FK field '%s' (attname='%s') from %s, target_model=%s",
        field_name,
        attname,
        obj.__class__.__name__,
        model_cls.__name__,
    )

    # Try direct attribute access (handles most cases)
    value = _get_fk_value_from_attname(obj, attname)

    if value is not None:
        return value

    # Value is None - determine if we should try fallback strategies
    logger.debug("FK attname '%s' is None, checking fallback options", attname)

    # Try accessing via relationship object
    value = _get_fk_value_from_relation(obj, field_name)

    if value is not None:
        return value

    # Last resort: try database refresh
    if not was_explicitly_set and obj.pk is not None:
        logger.debug(
            "Attempting DB refresh for field '%s'",
            field_name,
        )
        value = _fetch_field_from_db(obj, model_cls, attname)

    return value


def _get_fk_value_from_attname(
    obj: Model,
    attname: str,
) -> Any:
    """Get FK value directly from the _id attribute."""
    value = getattr(obj, attname, None)
    logger.debug("FK value from getattr('%s'): %s", attname, value)
    return value


def _get_fk_value_from_relation(obj: Model, field_name: str) -> Any:
    """Get FK value by accessing the relationship object and extracting its PK."""
    related_obj = getattr(obj, field_name, None)

    if related_obj is None:
        return None

    if not hasattr(related_obj, "pk"):
        logger.warning(
            "Related object for field '%s' exists but has no pk attribute",
            field_name,
        )
        return None

    pk_value = related_obj.pk
    logger.debug("FK value extracted from related object's pk: %s", pk_value)
    return pk_value


def _extract_regular_value(
    obj: Model,
    field_name: str,
    model_cls: type[Model],
) -> Any:
    """
    Extract value for a regular (non-FK) field.
    """
    was_explicitly_set = field_name in obj.__dict__
    value = getattr(obj, field_name, None)

    # For None values that weren't explicitly set, try fetching from the database
    should_try_fallback = value is None and not was_explicitly_set and obj.pk is not None

    if should_try_fallback:
        logger.debug(
            "Regular field '%s' is None, trying DB fallback",
            field_name,
        )
        value = _fetch_field_from_db(obj, model_cls, field_name)

    logger.debug(
        "Regular field '%s' extracted: %s (explicitly_set=%s)",
        field_name,
        value,
        was_explicitly_set,
    )
    return value


def _fetch_field_from_db(
    obj: Model,
    model_cls: type[Model],
    field_name: str,
) -> Any:
    """
    Fetch a field value from the database.

    Used as a last resort when a field value is not accessible through the instance.
    """
    if not hasattr(obj, "pk") or obj.pk is None:
        logger.debug("Cannot fetch from DB: object has no pk")
        return None

    try:
        parent_instance = model_cls.objects.filter(pk=obj.pk).only(field_name).first()

        if parent_instance is None:
            logger.warning(
                "No parent instance found in %s for pk=%s",
                model_cls.__name__,
                obj.pk,
            )
            return None

        value = getattr(parent_instance, field_name, None)
        logger.debug(
            "Field '%s' fetched from DB: %s",
            field_name,
            value,
        )
        return value

    except Exception as e:
        logger.error(
            "Failed to fetch field '%s' from DB for %s(pk=%s): %s",
            field_name,
            model_cls.__name__,
            obj.pk,
            e,
            exc_info=True,
        )
        return None


def _field_value_changed(field: Field, old_obj: Model, new_obj: Model) -> bool:
    """Check if a field value changed between two instances."""
    old_val = getattr(old_obj, field.name, None)
    new_val = getattr(new_obj, field.name, None)

    try:
        # Use field's get_prep_value for database-ready comparison
        # This handles timezone conversions, type coercions, etc.
        old_prep = field.get_prep_value(old_val)
        new_prep = field.get_prep_value(new_val)
        return old_prep != new_prep
    except (TypeError, ValueError, AttributeError) as e:
        # Fallback to direct comparison if get_prep_value fails
        logger.debug(
            "get_prep_value failed for field '%s': %s, using direct comparison",
            field.name,
            e,
        )
        return old_val != new_val


def _should_include_auto_field(field: Field, for_update: bool) -> bool:
    """Determine if an auto field should be included in a database operation."""
    has_auto_now = getattr(field, "auto_now", False)
    has_auto_now_add = getattr(field, "auto_now_add", False)

    if for_update:
        # Updates only include auto_now fields
        return has_auto_now

    # Creates include both auto_now and auto_now_add
    return has_auto_now or has_auto_now_add


def _pre_save_field_on_instances(
    field: Field,
    instances: Iterable[Model],
    for_update: bool,
) -> None:
    """Pre-save a field on multiple instances to update auto values."""
    add_flag = not for_update  # add=True for creates, add=False for updates

    for instance in instances:
        try:
            field.pre_save(instance, add=add_flag)
        except Exception as e:
            logger.error(
                "Failed to pre-save field '%s' on instance %s: %s",
                field.name,
                instance,
                e,
                exc_info=True,
            )


# ============================================================================
# Deprecated Functions (maintained for backward compatibility)
# ============================================================================


def get_auto_now_only_fields(model_cls: type[Model]) -> list[str]:
    """
    Get only auto_now fields (excluding auto_now_add).

    DEPRECATED: Use get_auto_fields(model_cls, include_auto_now_add=False) instead.
    """
    return get_auto_fields(model_cls, include_auto_now_add=False)


def collect_auto_now_fields_for_models(
    model_classes: Iterable[type[Model]],
) -> set[str]:
    """
    Collect auto_now fields across model classes.

    DEPRECATED: Use handle_auto_now_fields_for_models instead,
    which both collects fields AND pre-saves them.
    """
    all_auto_now = set()
    for model_cls in model_classes:
        all_auto_now.update(get_auto_fields(model_cls, include_auto_now_add=False))
    return all_auto_now


def pre_save_auto_now_fields(
    objects: Iterable[Model],
    model_classes: Iterable[type[Model]],
) -> None:
    """
    Pre-save auto_now fields across model classes.

    DEPRECATED: Use handle_auto_now_fields_for_models instead,
    which handles both collection and pre-saving in one call.
    """
    auto_now_fields = collect_auto_now_fields_for_models(model_classes)

    for field_name in auto_now_fields:
        for model_cls in model_classes:
            field = _get_field_or_none(model_cls, field_name)
            if field and getattr(field, "auto_now", False):
                for obj in objects:
                    try:
                        field.pre_save(obj, add=False)
                    except Exception as e:
                        logger.error(
                            "Failed to pre-save field '%s' on %s: %s",
                            field_name,
                            obj,
                            e,
                        )
                break
