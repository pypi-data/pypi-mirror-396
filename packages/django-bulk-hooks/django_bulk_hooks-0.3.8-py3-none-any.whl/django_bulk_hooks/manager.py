import logging

from django.db import models

from django_bulk_hooks.queryset import HookQuerySet


logger = logging.getLogger(__name__)


def _delegate_to_queryset(self, method_name, *args, **kwargs):
    """
    Generic delegation to queryset method.

    Args:
        method_name: Name of the method to call on the queryset
        *args, **kwargs: Arguments to pass to the method

    Returns:
        Result of the queryset method call
    """
    return getattr(self.get_queryset(), method_name)(*args, **kwargs)


class BulkHookManager(models.Manager):
    """
    Manager that provides hook-aware bulk operations.

    This manager automatically applies hook functionality to its querysets.
    It can be used as a base class or composed with other managers using
    the queryset-based approach.
    """

    def get_queryset(self):
        """
        Return a HookQuerySet for this manager.

        Uses the new with_hooks() method for better composition with other managers.
        """
        base_queryset = super().get_queryset()
        return HookQuerySet.with_hooks(base_queryset)

    def bulk_create(
        self,
        objs,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
        bypass_hooks=False,
        **kwargs,
    ):
        """
        Delegate to QuerySet's bulk_create implementation.
        This follows Django's pattern where Manager methods call QuerySet methods.
        """
        return _delegate_to_queryset(
            self,
            "bulk_create",
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
            bypass_hooks=bypass_hooks,
            **kwargs,
        )

    def bulk_update(
        self,
        objs,
        fields=None,
        bypass_hooks=False,
        **kwargs,
    ):
        """
        Delegate to QuerySet's bulk_update implementation.
        This follows Django's pattern where Manager methods call QuerySet methods.

        Note: Parameters like unique_fields, update_conflicts, update_fields, and ignore_conflicts
        are not supported by bulk_update and will be ignored with a warning.
        These parameters are only available in bulk_create for UPSERT operations.
        """
        # DEBUG: Log incoming fields parameter
        logger.error(f"🟪 MANAGER.bulk_update ENTRY: fields={fields}, objs count={len(objs) if objs else 0}, kwargs={kwargs}")

        if fields is not None:
            kwargs["fields"] = fields

        logger.error(f"🟪 MANAGER.bulk_update: Delegating to queryset with kwargs={kwargs}")
        return _delegate_to_queryset(
            self,
            "bulk_update",
            objs,
            bypass_hooks=bypass_hooks,
            **kwargs,
        )

    def bulk_delete(
        self,
        objs,
        batch_size=None,
        bypass_hooks=False,
        **kwargs,
    ):
        """
        Delegate to QuerySet's bulk_delete implementation.
        This follows Django's pattern where Manager methods call QuerySet methods.
        """
        return _delegate_to_queryset(
            self,
            "bulk_delete",
            objs,
            batch_size=batch_size,
            bypass_hooks=bypass_hooks,
            **kwargs,
        )

    def delete(self, bypass_hooks=False):
        """
        Delegate to QuerySet's delete implementation.
        This follows Django's pattern where Manager methods call QuerySet methods.
        """
        return _delegate_to_queryset(self, "delete", bypass_hooks=bypass_hooks)

    def update(self, bypass_hooks=False, **kwargs):
        """
        Delegate to QuerySet's update implementation.
        This follows Django's pattern where Manager methods call QuerySet methods.
        """
        return _delegate_to_queryset(self, "update", bypass_hooks=bypass_hooks, **kwargs)

    def save(self, obj, bypass_hooks=False):
        """
        Save a single object using the appropriate bulk operation.
        """
        if obj.pk:
            # bulk_update now auto-detects changed fields
            self.bulk_update([obj], bypass_hooks=bypass_hooks)
        else:
            self.bulk_create([obj], bypass_hooks=bypass_hooks)
        return obj
