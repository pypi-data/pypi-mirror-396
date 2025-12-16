from enum import Enum, IntEnum


class Priority(IntEnum):
    """
    Named priorities for django-bulk-hooks hooks.
    Replaces module-level constants with a clean IntEnum.
    """

    HIGHEST = 0  # runs first
    HIGH = 25  # runs early
    NORMAL = 50  # default ordering
    LOW = 75  # runs late
    LOWEST = 100  # runs last


DEFAULT_PRIORITY = Priority.NORMAL


class CommitStrategy(Enum):
    """
    Commit strategies for bulk operations.
    
    ATOMIC (Default):
    - Single transaction, all-or-nothing
    - Hooks see ALL objects
    - Compatible with all hooks
    - Compatible with upserts
    
    PER_BATCH:
    - Each batch in savepoint, fail-fast
    - ⚠️ Hooks see ONLY current batch
    - ⚠️ Incompatible with HasChanged, WasEqual, ChangesTo conditions
    - ⚠️ With update_conflicts: change detection limited to batch
    - ⚠️ Upsert metadata disabled (too complex with batching)
    
    BEST_EFFORT:
    - Like PER_BATCH but continues on errors
    - Uses binary search to identify failures (NO N+1)
    - ⚠️ All PER_BATCH limitations apply
    - ⚠️ Binary search disabled for upserts (metadata complexity)
    - Returns BulkCreateResult with detailed tracking
    """
    ATOMIC = "atomic"
    PER_BATCH = "per_batch"
    BEST_EFFORT = "best_effort"
