"""
HookQuerySet - Django QuerySet with hook support.

This is a thin coordinator that delegates all complex logic to services.
It follows the Facade pattern, providing a simple interface over the
complex coordination required for bulk operations with hooks.
"""

import logging

from django.db import models
from django.db import transaction

from django_bulk_hooks.helpers import extract_pks

logger = logging.getLogger(__name__)


class HookQuerySet(models.QuerySet):
    """
    QuerySet with hook support.

    This is a thin facade over BulkOperationCoordinator. It provides
    backward-compatible API for Django's QuerySet while integrating
    the full hook lifecycle.

    Key design principles:
    - Minimal logic (< 10 lines per method)
    - No business logic (delegate to coordinator)
    - No conditionals (let services handle it)
    - Transaction boundaries only
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._coordinator = None

    @classmethod
    def with_hooks(cls, queryset):
        """
        Apply hook functionality to any queryset.

        This enables hooks to work with any manager by applying hook
        capabilities at the queryset level rather than through inheritance.

        Args:
            queryset: Any Django QuerySet instance

        Returns:
            HookQuerySet instance with the same query parameters
        """
        if isinstance(queryset, cls):
            return queryset  # Already has hooks

        # Create a new HookQuerySet with the same parameters as the original queryset
        hook_qs = cls(
            model=queryset.model,
            query=queryset.query,
            using=queryset._db,
            hints=getattr(queryset, "_hints", {}),
        )

        # Preserve any additional attributes from the original queryset
        # This allows composition with other queryset enhancements
        cls._preserve_queryset_attributes(hook_qs, queryset)

        return hook_qs

    @classmethod
    def _preserve_queryset_attributes(cls, hook_qs, original_qs):
        """
        Preserve attributes from the original queryset.

        This enables composition with other queryset enhancements like
        queryable properties, annotations, etc.
        """
        # Copy non-method attributes that might be set by other managers
        for attr_name in dir(original_qs):
            if not attr_name.startswith("_") and not hasattr(cls, attr_name) and not callable(getattr(original_qs, attr_name, None)):
                try:
                    value = getattr(original_qs, attr_name)
                    setattr(hook_qs, attr_name, value)
                except (AttributeError, TypeError):
                    # Skip attributes that can't be copied
                    continue

    @property
    def coordinator(self):
        """Lazy initialization of coordinator"""
        if self._coordinator is None:
            from django_bulk_hooks.operations import BulkOperationCoordinator

            self._coordinator = BulkOperationCoordinator(self)
        return self._coordinator

    @transaction.atomic
    def bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
        bypass_hooks=False,
    ):
        """
        Create multiple objects with hook support.

        This is the public API - delegates to coordinator.
        """
        return self.coordinator.create(
            objs=objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
            bypass_hooks=bypass_hooks,
        )

    @transaction.atomic
    def bulk_update(
        self,
        objs,
        fields=None,
        batch_size=None,
        bypass_hooks=False,
        **kwargs,
    ):
        """
        Update multiple objects with hook support.

        This is the public API - delegates to coordinator.

        Args:
            objs: List of model instances to update
            fields: List of field names to update (optional, will auto-detect if None)
            batch_size: Number of objects per batch
            bypass_hooks: Skip all hooks if True

        Returns:
            Number of objects updated
        """
        # DEBUG: Log incoming fields parameter
        logger.debug(f"🟦 QUERYSET.bulk_update ENTRY: fields={fields}, objs count={len(objs) if objs else 0}")

        # If fields is None, auto-detect changed fields using analyzer
        if fields is None:
            fields = self.coordinator.analyzer.detect_changed_fields(objs)
            logger.debug(f"🟦 QUERYSET.bulk_update: Auto-detected fields={fields}")
            if not fields:
                return 0

        logger.debug(f"🟦 QUERYSET.bulk_update: Calling coordinator.update with fields={fields}")
        return self.coordinator.update(
            objs=objs,
            fields=fields,
            batch_size=batch_size,
            bypass_hooks=bypass_hooks,
        )

    @transaction.atomic
    def update(self, bypass_hooks=False, **kwargs):
        """
        Update QuerySet with hook support.

        This is the public API - delegates to coordinator.

        Args:
            bypass_hooks: Skip all hooks if True
            **kwargs: Fields to update

        Returns:
            Number of objects updated
        """
        return self.coordinator.update_queryset(
            update_kwargs=kwargs,
            bypass_hooks=bypass_hooks,
        )

    @transaction.atomic
    def bulk_delete(
        self,
        objs,
        bypass_hooks=False,
        **kwargs,
    ):
        """
        Delete multiple objects with hook support.

        This is the public API - delegates to coordinator.

        Args:
            objs: List of objects to delete
            bypass_hooks: Skip all hooks if True

        Returns:
            Tuple of (count, details dict)
        """
        # Filter queryset to only these objects
        pks = extract_pks(objs)
        if not pks:
            return 0

        # Create a filtered queryset
        filtered_qs = self.filter(pk__in=pks)

        # Use coordinator with the filtered queryset
        from django_bulk_hooks.operations import BulkOperationCoordinator

        coordinator = BulkOperationCoordinator(filtered_qs)

        count, details = coordinator.delete(
            bypass_hooks=bypass_hooks,
        )

        # For bulk_delete, return just the count to match Django's behavior
        return count

    @transaction.atomic
    def delete(self, bypass_hooks=False):
        """
        Delete QuerySet with hook support.

        This is the public API - delegates to coordinator.

        Args:
            bypass_hooks: Skip all hooks if True

        Returns:
            Tuple of (count, details dict)
        """
        return self.coordinator.delete(
            bypass_hooks=bypass_hooks,
        )
