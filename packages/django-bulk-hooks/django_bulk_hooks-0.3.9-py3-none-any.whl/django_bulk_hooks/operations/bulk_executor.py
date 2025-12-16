"""
Bulk executor service for database operations.

Coordinates bulk database operations with validation.
This service is the only component that directly calls Django ORM methods.
"""

import logging
import time
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

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

if TYPE_CHECKING:
    from django_bulk_hooks.enums import CommitStrategy
    from django_bulk_hooks.results import BulkCreateResult
    from django_bulk_hooks.results import BatchInfo
    from django_bulk_hooks.results import ObjectFailure

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

    # ==================== Batch Processing Methods ====================
    
    def _chunk_objects(self, objs: List[Model], chunk_size: int) -> List[List[Model]]:
        """
        Split objects into chunks. Single responsibility.
        
        Edge cases handled:
        - Empty list returns []
        - chunk_size <= 0 returns [objs]
        - chunk_size > len(objs) returns [objs]
        """
        if not objs:
            return []
        if chunk_size <= 0:
            return [objs]
        return [objs[i:i + chunk_size] for i in range(0, len(objs), chunk_size)]
    
    def _initialize_batch_result(
        self, objs: List[Model], commit_strategy: 'CommitStrategy', batch_size: int
    ) -> 'BulkCreateResult':
        """Initialize result object."""
        from django_bulk_hooks.results import BulkCreateResult
        return BulkCreateResult(
            objects=[],
            total_objects=len(objs),
            commit_strategy=commit_strategy.value,
            batch_size=batch_size,
            start_time=datetime.now(),
            failures=[],
            batch_info=[],
        )
    
    def _validate_batch_limits(self, chunks: List[List[Model]], limits: dict) -> None:
        """Validate batch operation meets safety limits."""
        if len(chunks) > limits['max_batches_per_operation']:
            raise ValueError(
                f"Operation requires {len(chunks)} batches, "
                f"exceeds limit of {limits['max_batches_per_operation']}"
            )
    
    def _log_batch_start(self, obj_count: int, batch_count: int, commit_strategy: 'CommitStrategy') -> None:
        """Log batch operation start."""
        logger.info(
            "Starting batch operation: %d objects in %d batches (strategy=%s)",
            obj_count, batch_count, commit_strategy.value
        )
        logger.warning(
            "Using %s: hooks see only current batch, not all %d objects",
            commit_strategy.value, obj_count
        )
    
    def _log_batch_completion(self, result: 'BulkCreateResult') -> None:
        """Log batch operation completion."""
        logger.info(
            "Batch operation completed: %d/%d succeeded (%.1f%%), %d failed, %.2fs",
            result.successful_count, result.total_objects, result.success_rate,
            result.failed_count, result.duration_seconds
        )
    
    def _check_failure_rate_threshold(self, result: 'BulkCreateResult', config: dict, batch_idx: int) -> None:
        """Check if failure rate exceeds threshold."""
        if not config['fail_fast'] or batch_idx < 5:
            return
        
        current_total = sum(b.batch_size for b in result.batch_info)
        if current_total == 0:
            return
        
        current_failure_rate = (len(result.failures) / current_total) * 100
        
        if current_failure_rate > config['max_failure_rate_percent']:
            raise ValueError(
                f"Failure rate {current_failure_rate:.1f}% exceeds "
                f"threshold {config['max_failure_rate_percent']}%"
            )
    
    def _retry_failed_batch_binary_search(
        self,
        chunk: List[Model],
        batch_index: int,
        operation_func: Callable,
        **operation_kwargs: Any,
    ) -> Tuple[List[Model], List['ObjectFailure']]:
        """
        Binary search to identify failures. NO N+1 queries.
        
        For 500 objects with 5 failures: ~9-12 operations, not 500.
        
        Transaction nesting strategy:
        - Level 1 (coordinator): Outer transaction for hook consistency
        - Level 2 (batch): Savepoint per batch for isolation
        - Level 3 (retry): Savepoint for binary search isolation
        
        Each level serves a distinct purpose. Django handles this correctly.
        """
        from django_bulk_hooks.results import ObjectFailure
        
        # Base case: single object
        if len(chunk) == 1:
            try:
                with transaction.atomic():
                    result = operation_func(chunk, **operation_kwargs)
                    return (result if isinstance(result, list) else [result], [])
            except Exception as e:
                failure = ObjectFailure(
                    obj=chunk[0],
                    error=e,
                    error_message=str(e),
                    batch_index=batch_index,
                )
                return ([], [failure])
        
        # Recursive: split in half
        mid = len(chunk) // 2
        all_successful = []
        all_failures = []
        
        for sub_chunk in [chunk[:mid], chunk[mid:]]:
            try:
                with transaction.atomic():
                    sub_result = operation_func(sub_chunk, **operation_kwargs)
                    if isinstance(sub_result, list):
                        all_successful.extend(sub_result)
                    else:
                        all_successful.append(sub_result)
            except Exception:
                logger.debug("Sub-batch of %d objects failed, splitting further", len(sub_chunk))
                sub_successful, sub_failures = self._retry_failed_batch_binary_search(
                    sub_chunk, batch_index, operation_func, **operation_kwargs
                )
                all_successful.extend(sub_successful)
                all_failures.extend(sub_failures)
        
        return (all_successful, all_failures)
    
    def _process_single_batch(
        self,
        chunk: List[Model],
        batch_idx: int,
        total_batches: int,
        commit_strategy: 'CommitStrategy',
        operation_func: Callable,
        monitoring: dict,
        is_upsert: bool,
        **operation_kwargs: Any,
    ) -> Tuple[List[Model], 'BatchInfo', List['ObjectFailure']]:
        """
        Process a single batch. Single responsibility.
        
        Returns: (successful_objects, batch_info, failures)
        """
        from django_bulk_hooks.enums import CommitStrategy
        from django_bulk_hooks.results import BatchInfo, ObjectFailure
        
        batch_start = time.time()
        batch_info = BatchInfo(
            batch_index=batch_idx,
            batch_size=len(chunk),
            successful_count=0,
            failed_count=0,
            duration_seconds=0.0,
        )
        
        try:
            with transaction.atomic():  # Savepoint
                chunk_objects = operation_func(chunk, **operation_kwargs)
                
                if isinstance(chunk_objects, list):
                    batch_info.successful_count = len(chunk_objects)
                    batch_info.duration_seconds = time.time() - batch_start
                    
                    if monitoring['log_batch_progress']:
                        logger.info(
                            "Batch %d/%d: %d objects in %.2fs",
                            batch_idx + 1, total_batches,
                            batch_info.successful_count, batch_info.duration_seconds
                        )
                    
                    return (chunk_objects, batch_info, [])
        
        except Exception as batch_error:
            batch_info.duration_seconds = time.time() - batch_start
            
            if commit_strategy == CommitStrategy.BEST_EFFORT:
                # CRITICAL: Disable binary search for upserts
                if is_upsert:
                    logger.warning(
                        "Batch %d/%d failed in upsert mode - binary search disabled, "
                        "marking entire batch as failed",
                        batch_idx + 1, total_batches
                    )
                    failures = [
                        ObjectFailure(
                            obj=obj,
                            error=batch_error,
                            error_message=f"Batch upsert failed: {str(batch_error)}",
                            batch_index=batch_idx,
                        )
                        for obj in chunk
                    ]
                    batch_info.failed_count = len(failures)
                    return ([], batch_info, failures)
                
                # Binary search retry (NO N+1) - only for non-upserts
                logger.warning(
                    "Batch %d/%d failed, using binary search (no N+1)",
                    batch_idx + 1, total_batches
                )
                
                retry_start = time.time()
                successful, failures = self._retry_failed_batch_binary_search(
                    chunk, batch_idx, operation_func, **operation_kwargs
                )
                retry_duration = time.time() - retry_start
                
                batch_info.successful_count = len(successful)
                batch_info.failed_count = len(failures)
                batch_info.duration_seconds += retry_duration
                
                logger.info(
                    "Binary search: %d succeeded, %d failed in %.2fs",
                    len(successful), len(failures), retry_duration
                )
                
                return (successful, batch_info, failures)
            else:
                # PER_BATCH - fail fast
                batch_info.failed_count = len(chunk)
                logger.error(
                    "Batch %d/%d failed, aborting: %s",
                    batch_idx + 1, total_batches, str(batch_error)
                )
                raise
        
        return ([], batch_info, [])
    
    def _process_in_batches(
        self,
        objs: List[Model],
        batch_size: int,
        commit_strategy: 'CommitStrategy',
        operation_func: Callable,
        is_upsert: bool = False,
        **operation_kwargs: Any,
    ) -> 'BulkCreateResult':
        """
        Coordinate batch processing. Delegates to focused functions.
        
        SOC: This orchestrates, doesn't implement details.
        """
        from django_bulk_hooks.enums import CommitStrategy
        from django_bulk_hooks.settings import get_setting
        
        if commit_strategy == CommitStrategy.ATOMIC:
            raise ValueError("ATOMIC handled at coordinator level")
        
        # Initialize
        result = self._initialize_batch_result(objs, commit_strategy, batch_size)
        chunks = self._chunk_objects(objs, batch_size)
        config = get_setting('ERROR_HANDLING')
        limits = get_setting('LIMITS')
        monitoring = get_setting('MONITORING')
        
        # Validate
        self._validate_batch_limits(chunks, limits)
        
        # Log start
        self._log_batch_start(len(objs), len(chunks), commit_strategy)
        
        # Process each batch (NOT N+1: each iteration is a bulk operation)
        for batch_idx, chunk in enumerate(chunks):
            batch_objects, batch_info, failures = self._process_single_batch(
                chunk, batch_idx, len(chunks), commit_strategy,
                operation_func, monitoring, is_upsert, **operation_kwargs
            )
            
            result.extend(batch_objects)
            result.failures.extend(failures)
            result.batch_info.append(batch_info)
            
            # Check failure rate
            self._check_failure_rate_threshold(result, config, batch_idx)
        
        # Finalize
        result.end_time = datetime.now()
        self._log_batch_completion(result)
        
        return result
    
    # ==================== End Batch Processing Methods ====================

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
        commit_strategy: Optional['CommitStrategy'] = None,
        **kwargs: Any,
    ) -> Union[List[Model], 'BulkCreateResult']:
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
            commit_strategy: Commit strategy (ATOMIC, PER_BATCH, BEST_EFFORT)
            **kwargs: Additional arguments

        Returns:
            List[Model] for ATOMIC mode, BulkCreateResult for batch modes
        """
        if not objs:
            return objs
        
        from django_bulk_hooks.enums import CommitStrategy
        from django_bulk_hooks.settings import get_setting
        
        # Default to ATOMIC
        if commit_strategy is None:
            commit_strategy = CommitStrategy.ATOMIC

        # CRITICAL: For upsert operations, remove auto_now_add fields from update_fields
        # New records will get created_at via auto_now_add, but existing records
        # should NOT have their created_at updated
        if update_conflicts and update_fields:
            update_fields = self._remove_auto_now_add_fields(update_fields, objs)
        
        # Check if using batch processing
        use_batch_processing = commit_strategy != CommitStrategy.ATOMIC
        
        if use_batch_processing:
            # Validate limits
            limits = get_setting('LIMITS')
            if len(objs) > limits['max_objects_per_operation']:
                raise ValueError(
                    f"Cannot process {len(objs)} objects, "
                    f"exceeds limit of {limits['max_objects_per_operation']}"
                )
            
            # Warn if upsert + batch mode
            if update_conflicts:
                logger.warning(
                    "Using %s with update_conflicts: "
                    "upsert metadata disabled, binary search disabled for failed batches",
                    commit_strategy.value
                )
            
            # Process in batches
            def single_batch_operation(chunk_objs, **op_kwargs):
                return self._execute_standard_bulk_create(
                    objs=chunk_objs,
                    batch_size=None,
                    ignore_conflicts=ignore_conflicts,
                    update_conflicts=update_conflicts,
                    update_fields=update_fields,
                    unique_fields=unique_fields,
                    **kwargs,
                )
            
            result = self._process_in_batches(
                objs=objs,
                batch_size=batch_size,
                commit_strategy=commit_strategy,
                operation_func=single_batch_operation,
                is_upsert=update_conflicts,
            )
            
            # Skip upsert metadata for batch modes (too complex)
            
            return result
        else:
            # ATOMIC mode - returns list
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
