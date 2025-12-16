"""
Django bulk hooks decorators for registering and managing hook behavior.

This module provides decorators for:
- Registering hooks on model events
- Preloading related fields to optimize database queries
- Registering bulk hooks with flexible signatures
"""

import inspect
import logging
from functools import wraps
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Set
from typing import Type
from typing import TypeVar

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import OneToOneField

from django_bulk_hooks.enums import DEFAULT_PRIORITY
from django_bulk_hooks.registry import register_hook

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class DecoratorError(Exception):
    """Base exception for decorator-related errors."""

    pass


class InvalidFieldNotationError(DecoratorError):
    """Raised when field notation is invalid."""

    pass


class MissingArgumentError(DecoratorError):
    """Raised when a required argument is missing."""

    pass


def hook(
    event: str, *, model: Type[models.Model], condition: Optional[Callable] = None, priority: int = DEFAULT_PRIORITY
) -> Callable[[F], F]:
    """
    Decorator to register multiple hooks on a method.

    Args:
        event: The event type to hook into
        model: The Django model class to monitor
        condition: Optional callable to determine if hook should execute
        priority: Execution priority (default: DEFAULT_PRIORITY)

    Returns:
        Decorated function with hook metadata attached

    Example:
        @hook('after_create', model=MyModel, priority=100)
        def my_hook(self, new_records, old_records, **kwargs):
            pass
    """

    def decorator(fn: F) -> F:
        if not hasattr(fn, "hooks_hooks"):
            fn.hooks_hooks = []
        fn.hooks_hooks.append((model, event, condition, priority))
        return fn

    return decorator


def select_related(*related_fields: str) -> Callable[[F], F]:
    """
    Decorator that preloads related fields on new_records before hook execution.

    This decorator optimizes database queries by prefetching related objects
    and populating Django's relation cache, avoiding N+1 query problems.

    Args:
        *related_fields: Field names using Django ORM notation (e.g., 'parent__child')

    Raises:
        InvalidFieldNotationError: If dot notation is used instead of __
        MissingArgumentError: If decorated function lacks 'new_records' parameter
        TypeError: If new_records is not a list

    Example:
        @select_related('author', 'category__parent')
        def my_hook(self, new_records, old_records, **kwargs):
            for record in new_records:
                print(record.author.name)  # No additional query
    """
    _validate_field_notation(related_fields)

    def decorator(func: F) -> F:
        sig = inspect.signature(func)
        preload_fn = _create_preload_function(related_fields)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if "new_records" not in bound.arguments:
                raise MissingArgumentError(f"@select_related requires a 'new_records' parameter in {func.__name__}")

            new_records = bound.arguments["new_records"]

            if not isinstance(new_records, list):
                raise TypeError(f"@select_related expects a list, got {type(new_records).__name__}")

            # Preloading is delegated to the dispatcher via the attached function
            return func(*args, **kwargs)

        wrapper._select_related_preload = preload_fn
        wrapper._select_related_fields = related_fields

        return wrapper

    return decorator


def bulk_hook(
    model_cls: Type[models.Model], event: str, when: Optional[Callable] = None, priority: Optional[int] = None
) -> Callable[[F], F]:
    """
    Decorator to register a bulk hook for a Django model.

    Supports both legacy and modern hook signatures for backward compatibility:
    - Legacy: func(new_records, old_records, **kwargs)
    - Modern: func(changeset, new_records, old_records, **kwargs)

    Args:
        model_cls: The Django model class to hook into
        event: The event to hook into (e.g., 'BEFORE_UPDATE', 'AFTER_CREATE')
        when: Optional condition callable determining if hook should run
        priority: Optional execution priority (default: DEFAULT_PRIORITY)

    Returns:
        Decorated function registered as a bulk hook

    Example:
        @bulk_hook(MyModel, 'after_update', priority=100)
        def my_bulk_hook(changeset, new_records, old_records, **kwargs):
            logger.info(f"Updated {len(new_records)} records")
    """

    def decorator(func: F) -> F:
        handler_cls = _create_handler_class(func)

        register_hook(
            model=model_cls,
            event=event,
            handler_cls=handler_cls,
            method_name="handle",
            condition=when,
            priority=priority or DEFAULT_PRIORITY,
        )

        func._bulk_hook_registered = True
        return func

    return decorator


# Private helper functions


def _validate_field_notation(fields: tuple) -> None:
    """Validate that fields use Django ORM __ notation instead of dot notation."""
    for field in fields:
        if "." in field:
            raise InvalidFieldNotationError(f"Invalid field notation '{field}'. Use Django ORM __ notation (e.g., 'parent__field')")


def _create_preload_function(related_fields: tuple) -> Callable:
    """Create the preload function used by the dispatcher."""

    def preload_related(
        records: List[models.Model], *, model_cls: Optional[Type[models.Model]] = None, skip_fields: Optional[Set[str]] = None
    ) -> None:
        """
        Preload related fields on model instances.

        Args:
            records: List of model instances to preload
            model_cls: Model class (inferred from records if not provided)
            skip_fields: Set of field names to skip preloading
        """
        if not isinstance(records, list):
            raise TypeError(f"Expected list of model instances, got {type(records).__name__}")

        if not records:
            return

        model_cls = model_cls or records[0].__class__
        skip_fields = skip_fields or set()

        validated_fields, direct_relations = _validate_and_extract_fields(related_fields, model_cls)

        if not validated_fields:
            return

        # Separate saved and unsaved records
        saved_records, unsaved_records = _partition_records(records)

        # Fetch related objects for saved records
        fetched_saved = _fetch_saved_related(saved_records, model_cls, validated_fields)

        # Fetch related objects for unsaved records
        fetched_unsaved = _fetch_unsaved_related(unsaved_records, direct_relations)

        # Populate the relation cache for all records
        _populate_relation_cache(records, fetched_saved, fetched_unsaved, direct_relations, related_fields, skip_fields)

    return preload_related


def _validate_and_extract_fields(fields: tuple, model_cls: Type[models.Model]) -> tuple:
    """
    Validate fields and extract direct relation metadata.

    Validates related fields for select_related usage.

    Returns:
        tuple: (validated_fields, direct_relation_fields)
    """
    logger.info(f"VALIDATE FIELDS: model={model_cls.__name__}, input_fields={fields}")

    expanded_fields = list(fields)

    direct_relation_fields = {}
    validated_fields = []

    for field in expanded_fields:
        if "__" in field:
            validated_fields.append(field)
            continue

        try:
            if not hasattr(model_cls, "_meta"):
                continue

            from django_bulk_hooks.operations.field_utils import _get_field_or_none

            relation_field = _get_field_or_none(model_cls, field)

            if relation_field is None:
                continue

            if _is_direct_relation(relation_field):
                validated_fields.append(field)
                direct_relation_fields[field] = relation_field

        except (FieldDoesNotExist, AttributeError) as e:
            logger.debug(f"Field '{field}' not found on {model_cls.__name__}: {e}")
            continue

    logger.info(f"VALIDATE FIELDS: validated={validated_fields}, direct_relations={list(direct_relation_fields.keys())}")
    return validated_fields, direct_relation_fields


def _is_direct_relation(field) -> bool:
    """Check if field is a direct relation (ForeignKey or OneToOne)."""
    return field.is_relation and not field.many_to_many and not field.one_to_many


def _partition_records(records: List[models.Model]) -> tuple:
    """
    Partition records into saved (with pk) and unsaved (without pk).

    Returns:
        tuple: (saved_record_ids, unsaved_records)
    """
    saved_ids = []
    unsaved = []

    for obj in records:
        if obj.pk is not None:
            if _needs_fetch(obj):
                saved_ids.append(obj.pk)
        else:
            unsaved.append(obj)

    return saved_ids, unsaved


def _needs_fetch(obj: models.Model) -> bool:
    """Determine if an object needs fetching based on its cache state."""
    if not hasattr(obj, "_state") or not hasattr(obj._state, "fields_cache"):
        return True

    try:
        # If fields_cache is not properly initialized, we need to fetch
        _ = obj._state.fields_cache
        return False
    except (TypeError, AttributeError):
        return True


def _fetch_saved_related(saved_ids: List[Any], model_cls: Type[models.Model], fields: List[str]) -> dict:
    """Fetch related objects for saved records using select_related."""
    if not saved_ids or not fields:
        return {}

    manager = getattr(model_cls, "_base_manager", None)
    if manager is None:
        return {}

    try:
        return manager.select_related(*fields).in_bulk(saved_ids)
    except Exception as e:
        logger.warning(f"Failed to fetch related objects for {model_cls.__name__}: {e}", exc_info=True)
        return {}


def _fetch_unsaved_related(unsaved_records: List[models.Model], direct_relations: dict) -> dict:
    """Fetch related objects for unsaved records by FK ID."""
    fetched_by_field = {field: {} for field in direct_relations}

    # Collect IDs to fetch for each relation
    ids_by_field = _collect_unsaved_ids(unsaved_records, direct_relations)

    # Fetch related objects for each field
    for field_name, related_ids in ids_by_field.items():
        if not related_ids:
            continue

        relation_field = direct_relations[field_name]
        related_model = getattr(relation_field.remote_field, "model", None)

        if related_model is None:
            continue

        manager = getattr(related_model, "_base_manager", None)
        if manager is None:
            continue

        try:
            fetched_by_field[field_name] = manager.in_bulk(related_ids)
        except Exception as e:
            logger.warning(f"Failed to fetch {related_model.__name__} instances: {e}", exc_info=True)

    return fetched_by_field


def _collect_unsaved_ids(unsaved_records: List[models.Model], direct_relations: dict) -> dict:
    """Collect FK IDs from unsaved records."""
    ids_by_field = {field: set() for field in direct_relations}

    for obj in unsaved_records:
        fields_cache = _get_fields_cache(obj)

        for field_name, relation_field in direct_relations.items():
            if fields_cache and field_name in fields_cache:
                continue

            try:
                related_id = getattr(obj, relation_field.get_attname(), None)
                if related_id is not None:
                    ids_by_field[field_name].add(related_id)
            except AttributeError:
                continue

    return ids_by_field


def _populate_relation_cache(
    records: List[models.Model],
    fetched_saved: dict,
    fetched_unsaved: dict,
    direct_relations: dict,
    all_fields: tuple,
    skip_fields: Set[str],
) -> None:
    """Populate the relation cache for all records."""
    for obj in records:
        fields_cache = _get_fields_cache(obj)

        if obj.pk is not None:
            _populate_saved_record(obj, fetched_saved, all_fields, direct_relations, fields_cache, skip_fields)
        else:
            _populate_unsaved_record(obj, fetched_unsaved, direct_relations, fields_cache, skip_fields)


def _populate_saved_record(
    obj: models.Model, fetched_saved: dict, all_fields: tuple, direct_relations: dict, fields_cache: Optional[dict], skip_fields: Set[str]
) -> None:
    """Populate relation cache for a saved record."""
    preloaded = fetched_saved.get(obj.pk)
    if not preloaded:
        return

    for field in all_fields:
        if field in skip_fields:
            continue

        if fields_cache and field in fields_cache:
            continue

        relation_field = direct_relations.get(field)
        if relation_field is None and "__" not in field:
            continue

        try:
            rel_obj = getattr(preloaded, field)
            _set_relation(obj, field, rel_obj, fields_cache)
        except AttributeError as e:
            logger.debug(f"Failed to get attribute '{field}' from preloaded object: {e}")


def _populate_unsaved_record(
    obj: models.Model, fetched_unsaved: dict, direct_relations: dict, fields_cache: Optional[dict], skip_fields: Set[str]
) -> None:
    """Populate relation cache for an unsaved record."""
    for field_name, relation_field in direct_relations.items():
        if field_name in skip_fields:
            continue

        if fields_cache and field_name in fields_cache:
            continue

        try:
            related_id = getattr(obj, relation_field.get_attname(), None)
        except AttributeError:
            continue

        if related_id is None:
            continue

        rel_obj = fetched_unsaved[field_name].get(related_id)
        if rel_obj is not None:
            _set_relation(obj, field_name, rel_obj, fields_cache)


def _get_fields_cache(obj: models.Model) -> Optional[dict]:
    """Safely get the fields cache from a model instance."""
    if hasattr(obj, "_state") and hasattr(obj._state, "fields_cache"):
        return obj._state.fields_cache
    return None


def _set_relation(obj: models.Model, field_name: str, rel_obj: models.Model, fields_cache: Optional[dict]) -> None:
    """Set a relation on an object and update its cache."""
    setattr(obj, field_name, rel_obj)
    if fields_cache is not None:
        fields_cache[field_name] = rel_obj


def _create_handler_class(func: Callable) -> Type:
    """
    Create a handler class that wraps a function for hook registration.

    Supports both legacy and modern signatures for backward compatibility.
    """

    class FunctionHandler:
        """Wrapper class for function-based bulk hooks."""

        def __init__(self):
            self.func = func
            self._sig = inspect.signature(func)
            self._params = list(self._sig.parameters.keys())

        def handle(self, changeset=None, new_records=None, old_records=None, **kwargs) -> Any:
            """
            Execute the hook function with appropriate signature.

            Automatically detects whether the function uses:
            - Modern signature: func(changeset, new_records, old_records, **kwargs)
            - Legacy signature: func(new_records, old_records, **kwargs)
            """
            if "changeset" in self._params:
                # Modern signature with explicit changeset parameter
                return self.func(changeset, new_records, old_records, **kwargs)

            # Legacy signature - decide whether to include changeset in kwargs
            if self._accepts_kwargs():
                kwargs["changeset"] = changeset
                return self.func(new_records, old_records, **kwargs)

            # Function doesn't accept **kwargs, use positional args only
            return self.func(new_records, old_records)

        def _accepts_kwargs(self) -> bool:
            """Check if function accepts **kwargs."""
            return any(param.kind == inspect.Parameter.VAR_KEYWORD for param in self._sig.parameters.values())

    return FunctionHandler
