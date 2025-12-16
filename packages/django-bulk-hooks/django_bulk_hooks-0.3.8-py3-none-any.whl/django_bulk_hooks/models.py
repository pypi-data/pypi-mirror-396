"""Django model mixin providing hook functionality for bulk operations."""

import logging
from typing import Any, List, Optional

from django.db import models

from django_bulk_hooks.manager import BulkHookManager

logger = logging.getLogger(__name__)


class HookModelMixin(models.Model):
    """
    Abstract model mixin that integrates hook functionality into Django models.

    This mixin overrides save(), delete(), and clean() to delegate to bulk
    operations that trigger appropriate hooks for validation, creation,
    updating, and deletion.

    Features:
    - Automatic hook triggering for CRUD operations
    - Bypass mechanism for hook-free operations
    - Proper validation hook integration

    Usage:
        class MyModel(HookModelMixin):
            name = models.CharField(max_length=100)

        # Hooks will fire automatically
        obj = MyModel(name="test")
        obj.save()

        # Bypass hooks when needed
        obj.save(bypass_hooks=True)
    """

    objects = BulkHookManager()

    class Meta:
        abstract = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Guard against accidental concrete parent inheritance
        if getattr(getattr(cls, "_meta", None), "abstract", False):
            return
        # If any concrete parents exist, inheritance is not supported
        parents = getattr(getattr(cls, "_meta", None), "parents", {}) or {}
        for parent in parents.keys():
            if not getattr(parent._meta, "abstract", False) and not getattr(parent._meta, "proxy", False):
                raise ValueError(
                    f"Concrete model inheritance is not supported by django-bulk-hooks. "
                    f"Model '{cls.__name__}' inherits from concrete model '{parent.__name__}'. "
                    f"Use abstract base models instead."
                )

    def save(
        self,
        *args: Any,
        bypass_hooks: bool = False,
        force_insert: bool = False,
        force_update: bool = False,
        update_fields: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "HookModelMixin":
        """
        Save the model instance with hook support.

        Delegates to bulk_create or bulk_update depending on whether this
        is a new instance. All hook logic is handled by the bulk operations.

        Args:
            bypass_hooks: If True, use Django's default save without hooks
            force_insert: Force INSERT operation
            force_update: Force UPDATE operation
            update_fields: List of field names to update (None = all fields)
            *args: Additional positional arguments for Django's save()
            **kwargs: Additional keyword arguments for Django's save()

        Returns:
            Self for method chaining

        Raises:
            ValueError: If force_insert and force_update are both True
        """
        if bypass_hooks:
            return super().save(*args, force_insert=force_insert, force_update=force_update, update_fields=update_fields, **kwargs)

        is_create = self.pk is None

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Save operation started: model=%s, pk=%s, is_create=%s, fields=%s",
                self.__class__.__name__,
                self.pk,
                is_create,
                list(self.__dict__.keys()),
            )

        if is_create:
            return self._handle_create()

        return self._handle_update(update_fields)

    def clean(self, bypass_hooks: bool = False) -> None:
        """
        Perform model validation with optional hook triggering.

        This method is called by Django during form validation (e.g., in admin).
        It triggers VALIDATE_* hooks unless bypassed.

        Args:
            bypass_hooks: If True, skip validation hooks

        Raises:
            ValidationError: If validation fails
        """
        super().clean()

        if bypass_hooks:
            return

        is_create = self.pk is None
        coordinator = self.__class__.objects.get_queryset().coordinator
        coordinator.clean([self], is_create=is_create)

    def _handle_create(self) -> "HookModelMixin":
        """
        Handle creation via bulk_create.

        Returns:
            The created instance with populated pk
        """
        # Use bulk_create for proper hook triggering
        result = self.__class__.objects.bulk_create([self])
        return result[0] if result else self

    def _handle_update(self, update_fields: Optional[List[str]]) -> "HookModelMixin":
        """
        Handle update via bulk_update.

        Args:
            update_fields: Fields to update, or None for all non-auto fields

        Returns:
            Self for method chaining
        """
        if update_fields is None:
            update_fields = self._get_updatable_fields()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Update fields determined: count=%d, fields=%s",
                len(update_fields),
                update_fields,
            )
            self._log_foreign_key_state(update_fields)

        self.__class__.objects.bulk_update([self], update_fields)
        return self

    def _get_updatable_fields(self) -> List[str]:
        """
        Get list of fields that should be updated.

        Excludes auto-created fields and the primary key.

        Returns:
            List of field names suitable for bulk_update
        """
        return [field.name for field in self.__class__._meta.fields if not field.auto_created and field.name != "id"]

    def _log_foreign_key_state(self, update_fields: List[str]) -> None:
        """
        Log the state of foreign key fields for debugging.

        Args:
            update_fields: Fields being updated
        """
        for field in self.__class__._meta.fields:
            if field.get_internal_type() != "ForeignKey":
                continue

            if field.name not in update_fields:
                continue

            fk_id_value = getattr(self, field.attname, None)
            fk_obj_value = getattr(self, field.name, None)

            logger.debug(
                "Foreign key state: field=%s, id_attr=%s, id_value=%s, obj_attr=%s, obj_value=%s, obj_has_pk=%s",
                field.name,
                field.attname,
                fk_id_value,
                field.name,
                fk_obj_value,
                hasattr(fk_obj_value, "pk") if fk_obj_value is not None else False,
            )

    def delete(self, *args: Any, bypass_hooks: bool = False, **kwargs: Any) -> tuple:
        """
        Delete the model instance with hook support.

        Delegates to bulk_delete which handles all hook logic.

        Args:
            bypass_hooks: If True, use Django's default delete without hooks
            *args: Additional positional arguments for Django's delete()
            **kwargs: Additional keyword arguments for Django's delete()

        Returns:
            Tuple of (number_deleted, dict_of_deletions_by_model)
        """
        if bypass_hooks:
            return super().delete(*args, **kwargs)

        return self.__class__.objects.filter(pk=self.pk).delete()
