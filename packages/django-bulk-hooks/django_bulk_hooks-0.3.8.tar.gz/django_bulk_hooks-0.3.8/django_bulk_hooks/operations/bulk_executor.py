"""
Bulk executor service for database operations.

Coordinates bulk database operations with validation.
This service is the only component that directly calls Django ORM methods.
"""

import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from django.db import transaction
from django.db.models import AutoField
from django.db.models import Case
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import QuerySet
from django.db.models import Value
from django.db.models import When
from django.db.models.constants import OnConflict
from django.db.models.functions import Cast

from django_bulk_hooks.helpers import tag_upsert_metadata
from django_bulk_hooks.operations.field_utils import get_field_value_for_db
from django_bulk_hooks.operations.field_utils import handle_auto_now_fields

logger = logging.getLogger(__name__)


class BulkExecutor:
    """
    Executes bulk database operations.

    Coordinates validation and database operations.
    This is the only service that directly calls Django ORM methods.

    All dependencies are explicitly injected via constructor for testability.
    """

    def __init__(
        self,
        queryset: QuerySet,
        analyzer: Any,
        record_classifier: Any,
    ) -> None:
        """
        Initialize bulk executor with explicit dependencies.

        Args:
            queryset: Django QuerySet instance
            analyzer: ModelAnalyzer instance (validation and field tracking)
            record_classifier: RecordClassifier instance
        """
        self.queryset = queryset
        self.analyzer = analyzer
        self.record_classifier = record_classifier
        self.model_cls = queryset.model

    def bulk_create(
        self,
        objs: List[Model],
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        update_fields: Optional[List[str]] = None,
        unique_fields: Optional[List[str]] = None,
        existing_record_ids: Optional[Set[int]] = None,
        existing_pks_map: Optional[Dict[int, int]] = None,
        **kwargs: Any,
    ) -> List[Model]:
        """
        Execute bulk create operation.

        NOTE: Coordinator validates inputs before calling this method.
        This executor trusts that inputs are pre-validated.

        Args:
            objs: Model instances to create (pre-validated)
            batch_size: Objects per batch
            ignore_conflicts: Whether to ignore conflicts
            update_conflicts: Whether to update on conflict
            update_fields: Fields to update on conflict
            unique_fields: Fields for conflict detection
            existing_record_ids: Pre-classified existing record IDs
            existing_pks_map: Pre-classified existing PK mapping
            **kwargs: Additional arguments

        Returns:
            List of created/updated objects
        """
        if not objs:
            return objs

        # CRITICAL: For upsert operations, remove auto_now_add fields from update_fields
        # New records will get created_at via auto_now_add, but existing records
        # should NOT have their created_at updated
        if update_conflicts and update_fields:
            update_fields = self._remove_auto_now_add_fields(update_fields, objs)

        # Execute standard bulk create
        result = self._execute_standard_bulk_create(
            objs=objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
            **kwargs,
        )

        # Tag upsert metadata
        self._handle_upsert_metadata_tagging(
            result_objects=result,
            objs=objs,
            update_conflicts=update_conflicts,
            unique_fields=unique_fields,
            existing_record_ids=existing_record_ids,
            existing_pks_map=existing_pks_map,
        )

        return result

    def bulk_update(self, objs: List[Model], fields: List[str], batch_size: Optional[int] = None) -> int:
        """
        Execute bulk update operation.

        NOTE: Coordinator validates inputs before calling this method.
        This executor trusts that inputs are pre-validated.

        Args:
            objs: Model instances to update (pre-validated)
            fields: Field names to update
            batch_size: Objects per batch

        Returns:
            Number of objects updated
        """
        # DEBUG: Log incoming fields parameter
        logger.debug("EXECUTOR.bulk_update ENTRY: fields=%s, objs count=%s", fields, len(objs))

        if not objs:
            return 0

        # Debug: Check FK values at bulk_update entry point
        for obj in objs:
            logger.debug(
                "BULK_UPDATE_ENTRY: obj.pk=%s, business_id in __dict__=%s, value=%s",
                getattr(obj, "pk", "None"),
                "business_id" in obj.__dict__,
                obj.__dict__.get("business_id", "NOT_IN_DICT"),
            )

        # Ensure auto_now fields are included
        logger.debug("EXECUTOR.bulk_update: Before _add_auto_now_fields, fields=%s", fields)
        fields = self._add_auto_now_fields(fields, objs)
        logger.debug("EXECUTOR.bulk_update: After _add_auto_now_fields, fields=%s", fields)

        # CRITICAL: Remove auto_now_add fields (like created_at) from fields list
        # These should NEVER be updated - they're only set on creation
        fields = self._remove_auto_now_add_fields(fields, objs)

        # Debug: Show final fields and object state before actual bulk_update
        logger.debug("BULK_UPDATE DEBUG: Final fields list: %s", fields)
        logger.debug("BULK_UPDATE DEBUG: Object PKs: %s", [obj.pk for obj in objs[:3]])
        for obj in objs[:1]:  # Just first object
            logger.debug("BULK_UPDATE DEBUG: Object __dict__ keys: %s", list(obj.__dict__.keys()))
            logger.debug("BULK_UPDATE DEBUG: month value: %s", getattr(obj, "month", "NO_ATTR"))
            logger.debug("BULK_UPDATE DEBUG: is_qualified value: %s", getattr(obj, "is_qualified", "NO_ATTR"))

        # Execute standard bulk update
        base_qs = self._get_base_queryset()
        return base_qs.bulk_update(objs, fields, batch_size=batch_size)

    def delete_queryset(self) -> Tuple[int, Dict[str, int]]:
        """
        Execute delete on the queryset.

        NOTE: Coordinator validates inputs before calling this method.

        Returns:
            Tuple of (count, details dict)
        """
        if not self.queryset:
            return 0, {}

        return QuerySet.delete(self.queryset)

    # ==================== Private: Create Helpers ====================

    def _execute_standard_bulk_create(
        self,
        objs: List[Model],
        batch_size: Optional[int],
        ignore_conflicts: bool,
        update_conflicts: bool,
        update_fields: Optional[List[str]],
        unique_fields: Optional[List[str]],
        **kwargs: Any,
    ) -> List[Model]:
        """Execute Django's native bulk_create."""
        base_qs = self._get_base_queryset()

        return base_qs.bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )

    def _handle_upsert_metadata_tagging(
        self,
        result_objects: List[Model],
        objs: List[Model],
        update_conflicts: bool,
        unique_fields: Optional[List[str]],
        existing_record_ids: Optional[Set[int]],
        existing_pks_map: Optional[Dict[int, int]],
    ) -> None:
        """
        Tag upsert metadata on result objects.

        Args:
            result_objects: Objects returned from bulk operation
            objs: Original objects passed to bulk_create
            update_conflicts: Whether this was an upsert operation
            unique_fields: Fields used for conflict detection
            existing_record_ids: Pre-classified existing record IDs
            existing_pks_map: Pre-classified existing PK mapping
        """
        if not (update_conflicts and unique_fields):
            return

        # Classify if needed
        if existing_record_ids is None or existing_pks_map is None:
            existing_record_ids, existing_pks_map = self.record_classifier.classify_for_upsert(objs, unique_fields)

        tag_upsert_metadata(result_objects, existing_record_ids, existing_pks_map)

    # ==================== Private: Update Helpers ====================

    def _add_auto_now_fields(self, fields: List[str], objs: List[Model]) -> List[str]:
        """
        Add auto_now fields to update list.

        Args:
            fields: Original field list
            objs: Objects being updated

        Returns:
            Field list with auto_now fields included
        """
        fields = list(fields)  # Copy to avoid mutation

        # Handle auto_now fields for current model
        auto_now_fields = handle_auto_now_fields(self.model_cls, objs, for_update=True)

        # Add to fields list if not present
        for auto_now_field in auto_now_fields:
            if auto_now_field not in fields:
                fields.append(auto_now_field)

        return fields

    def _remove_auto_now_add_fields(self, fields: List[str], objs: List[Model]) -> List[str]:
        """
        Remove auto_now_add fields from the fields list.

        These fields should NEVER be updated - they're only set on creation.
        This is critical for:
        1. Regular bulk_update operations
        2. Upsert operations (bulk_create with update_conflicts=True)

        Args:
            fields: Field list to filter
            objs: Objects being updated (to determine model class)

        Returns:
            Field list with auto_now_add fields removed
        """
        if not objs or not fields:
            return fields

        model_cls = objs[0].__class__
        auto_now_add_fields = set()

        for field in model_cls._meta.local_fields:
            if getattr(field, "auto_now_add", False):
                auto_now_add_fields.add(field.name)

        if not auto_now_add_fields:
            return fields

        # Remove auto_now_add fields from the list
        filtered_fields = [f for f in fields if f not in auto_now_add_fields]

        if filtered_fields != fields:
            removed = set(fields) - set(filtered_fields)
            logger.debug(
                "Removed auto_now_add fields from update fields list: %s. These fields should only be set on creation, not update.", removed
            )

        return filtered_fields

    # ==================== Private: Utilities ====================

    # ==================== Private: Utilities ====================

    def _get_base_queryset(self) -> QuerySet:
        """Get base Django QuerySet to avoid recursion."""
        return QuerySet(model=self.model_cls, using=self.queryset.db)
