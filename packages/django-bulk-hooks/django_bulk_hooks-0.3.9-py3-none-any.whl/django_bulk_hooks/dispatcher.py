"""
HookDispatcher: Deterministic, priority-ordered hook execution system.

Provides a single execution path for all hooks with proper lifecycle management.
"""

import logging
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

logger = logging.getLogger(__name__)

from django_bulk_hooks.dispatcher_executor import ConditionAnalyzer
from django_bulk_hooks.dispatcher_executor import HookExecutor
from django_bulk_hooks.dispatcher_preloader import RelationshipPreloader

## OperationKey removed (dedup no longer required)


## RelationshipPreloader moved to django_bulk_hooks.dispatcher_preloader


## ConditionAnalyzer moved to django_bulk_hooks.dispatcher_executor


class HookDispatcher:
    """
    Per-operation hook dispatcher with automatic cleanup.

    Following Salesforce's trigger context pattern:
    - Each operation gets a fresh dispatcher instance
    - Context is isolated (no cross-operation state leakage)
    - Automatically garbage collected when operation completes

    Responsibilities:
    - Execute hooks in priority order
    - Filter records based on conditions
    - Provide ChangeSet context to hooks
    - Fail-fast error propagation
    - Manage complete operation lifecycle (VALIDATE, BEFORE, AFTER)

    Design:
        No global singleton - create one per bulk operation.
        This prevents memory leaks in long-lived processes (web servers).
    """

    # Class-level constant for bounded cache
    MAX_PRELOADER_CACHE_SIZE = 50

    def __init__(self, registry):
        """
        Initialize a dispatcher for a single operation.

        Creates an isolated context similar to Salesforce's per-transaction
        trigger context. State is automatically cleaned up when the operation
        completes and this instance is garbage collected.

        Args:
            registry: Hook registry providing get_hooks method
        """
        self.registry = registry

        # Per-operation state (cleared when dispatcher is GC'd)
        self._executed_hooks: Set[Tuple] = set()

        # Bounded cache with automatic eviction to prevent unbounded growth
        self._preloader_cache: dict = {}

    def _reset_executed_hooks(self):
        """
        Reset the executed hooks tracking set.

        Called at the start of each operation to ensure clean state.
        """
        self._executed_hooks.clear()

    def _get_or_create_preloader(self, model_cls):
        """
        Get or create a preloader with bounded cache and automatic eviction.

        Prevents unbounded memory growth by evicting the oldest entry
        when cache exceeds MAX_PRELOADER_CACHE_SIZE.

        Args:
            model_cls: Django model class

        Returns:
            RelationshipPreloader instance for the model
        """
        if model_cls in self._preloader_cache:
            return self._preloader_cache[model_cls]

        # Create new preloader
        preloader = RelationshipPreloader(model_cls)
        self._preloader_cache[model_cls] = preloader

        # Evict oldest entry if cache is full (simple FIFO eviction)
        if len(self._preloader_cache) > self.MAX_PRELOADER_CACHE_SIZE:
            # Remove first item (oldest insertion)
            first_key = next(iter(self._preloader_cache))
            del self._preloader_cache[first_key]
            logger.debug(f"Preloader cache exceeded {self.MAX_PRELOADER_CACHE_SIZE} entries, evicted {first_key.__name__}")

        return preloader

    def execute_operation_with_hooks(
        self,
        changeset,
        operation: Callable,
        event_prefix: str,
        bypass_hooks: bool = False,
    ):
        """
        Execute operation with full hook lifecycle.

        Lifecycle:
        1. VALIDATE_{event}
        2. BEFORE_{event}
        3. Actual operation
        4. AFTER_{event}

        Args:
            changeset: ChangeSet for the operation
            operation: Callable performing the DB operation
            event_prefix: 'create', 'update', or 'delete'
            bypass_hooks: Skip all hooks if True

        Returns:
            Result of operation
        """
        if bypass_hooks:
            return operation()

        try:
            # VALIDATE phase
            self.dispatch(changeset, f"validate_{event_prefix}")

            # BEFORE phase
            self.dispatch(changeset, f"before_{event_prefix}")

            # Execute operation
            result = operation()

            # AFTER phase - rebuild changeset for create operations
            after_changeset = self._prepare_after_changeset(
                changeset,
                result,
                event_prefix,
            )
            self.dispatch(after_changeset, f"after_{event_prefix}")

            return result
        finally:
            pass

    def dispatch(
        self,
        changeset,
        event: str,
        bypass_hooks: bool = False,
    ) -> None:
        """
        Dispatch hooks for a changeset with deterministic ordering.

        This is the single execution path for ALL hooks.

        Args:
            changeset: ChangeSet instance with record changes
            event: Event name (e.g., 'after_update', 'before_create')
            bypass_hooks: Skip all hook execution if True

        Raises:
            Exception: Any exception raised by a hook (fails fast)
        """
        if bypass_hooks:
            return

        # Get hooks sorted by priority (including abstract base hooks)
        # Prefer abstract-inclusive lookup; fall back to standard get_hooks if empty
        try:
            hooks = self.registry.get_hooks_including_abstract(changeset.model_cls, event)
        except Exception:
            hooks = []
        if not hooks:
            hooks = self.registry.get_hooks(changeset.model_cls, event)

        logger.debug(f"Dispatching: model={changeset.model_cls.__name__}, event={event}, hooks_found={len(hooks)}")

        if not hooks:
            return

        # Execute hooks
        logger.info(f"Executing {len(hooks)} hooks for {changeset.model_cls.__name__}.{event}")

        executor = HookExecutor(changeset.model_cls)

        for handler_cls, method_name, condition, priority in hooks:
            logger.info(f"  → {handler_cls.__name__}.{method_name} (priority={priority})")
            executor.execute(handler_cls, method_name, condition, changeset, event)

    def preload_relationships(self, changeset, relationships: Set[str]) -> None:
        """
        Preload relationships for a changeset before hook execution.

        This is called by the coordinator to bulk-preload all relationships needed
        by hook conditions for an operation.

        Optimized to use a single query when new_records and old_records have
        overlapping PKs (common in update operations).

        Args:
            changeset: ChangeSet instance with record changes
            relationships: Set of relationship field names to preload
        """
        if not relationships:
            return

        # Get or create preloader for this model
        model_cls = changeset.model_cls
        preloader = self._get_or_create_preloader(model_cls)

        logger.info(f"BULK PRELOAD: Preloading {len(relationships)} relationships for {model_cls.__name__}: {relationships}")

        # Optimization: Check if we can batch both new and old records together
        new_records = changeset.new_records or []
        old_records = changeset.old_records or []

        if new_records and old_records:
            # Collect all unique PKs from both sets
            new_pks = {r.pk for r in new_records if r.pk is not None}
            old_pks = {r.pk for r in old_records if r.pk is not None}

            # If there's significant overlap (>30%), batch them together
            overlap = new_pks & old_pks
            if overlap and len(overlap) / max(len(new_pks), len(old_pks)) > 0.3:
                logger.info(f"BULK PRELOAD OPTIMIZATION: Batching {len(new_pks | old_pks)} records (overlap: {len(overlap)})")
                self._batch_preload_records(preloader, model_cls, new_records, old_records, relationships)
                return

        # Standard path: separate preloading for new and old records
        # Preload for new_records (preserve FK values for user changes)
        if new_records:
            preloader.preload_for_records(
                new_records,
                relationships,
                preserve_fk_values=True,
            )

        # Preload for old_records (don't preserve - reflect DB state)
        if old_records:
            preloader.preload_for_records(
                old_records,
                relationships,
                preserve_fk_values=False,
            )

    def _batch_preload_records(
        self,
        preloader,
        model_cls,
        new_records: List,
        old_records: List,
        relationships: Set[str],
    ) -> None:
        """
        Batch preload relationships for both new and old records in a single query.

        This optimization combines PKs from both sets and fetches all related
        objects in one query, then distributes them to the appropriate records.

        Args:
            preloader: RelationshipPreloader instance
            model_cls: Model class
            new_records: List of new record instances
            old_records: List of old record instances
            relationships: Set of relationship field names to preload
        """
        # Collect all PKs
        all_pks = set()
        for record in new_records:
            if record.pk is not None:
                all_pks.add(record.pk)
        for record in old_records:
            if record.pk is not None:
                all_pks.add(record.pk)

        if not all_pks:
            return

        # Single bulk query for all records
        preloaded_map = model_cls.objects.filter(pk__in=all_pks).select_related(*relationships).in_bulk()

        logger.debug(f"Batched preload fetched {len(preloaded_map)} records for {len(all_pks)} PKs")

        # Attach relationships to new_records (preserve FK values)
        for record in new_records:
            if record.pk in preloaded_map:
                preloaded_record = preloaded_map[record.pk]
                preloader._attach_relationships(
                    record,
                    preloaded_record,
                    relationships,
                    preserve_fk_values=True,
                )

        # Attach relationships to old_records (don't preserve)
        for record in old_records:
            if record.pk in preloaded_map:
                preloaded_record = preloaded_map[record.pk]
                preloader._attach_relationships(
                    record,
                    preloaded_record,
                    relationships,
                    preserve_fk_values=False,
                )

    def _prepare_after_changeset(self, changeset, result, event_prefix: str):
        """Prepare changeset for AFTER hooks, rebuilding if needed."""
        if result and isinstance(result, list) and event_prefix == "create":
            # For create, rebuild changeset with assigned PKs
            from django_bulk_hooks.helpers import build_changeset_for_create

            return build_changeset_for_create(changeset.model_cls, result)
        return changeset

    # Dedup/reset removed

    def _extract_condition_relationships(self, condition, model_cls) -> Set[str]:
        """
        Extract relationship paths that a condition might access.

        Args:
            condition: HookCondition instance
            model_cls: Model class for context

        Returns:
            Set of relationship field names to preload
        """
        analyzer = ConditionAnalyzer(model_cls)
        return analyzer.extract_relationships(condition)
