"""Result objects for bulk operations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ObjectFailure:
    """
    Record of a failed object. Memory-efficient.
    """
    obj: Any
    error: Exception
    error_message: str
    batch_index: int
    
    def __repr__(self):
        return f"<ObjectFailure: {self.error_message}>"


@dataclass
class BatchInfo:
    """Metadata for a single batch."""
    batch_index: int
    batch_size: int
    successful_count: int
    failed_count: int
    duration_seconds: float
    
    @property
    def success_rate(self) -> float:
        if self.batch_size == 0:
            return 100.0
        return (self.successful_count / self.batch_size) * 100.0


class BulkCreateResult(list):
    """
    Result from bulk_create with batch processing.
    
    Inherits from list for 100% backward compatibility.
    
    Memory considerations:
    - Successful objects: Kept in list (required for backward compat)
    - Failures: Only metadata tracked (obj reference + error)
    - For 500k objects: estimate 10-50MB depending on model
    - Max limit enforced via settings (default 500k objects)
    
    Usage:
        result = Model.objects.bulk_create(objs, commit_strategy=...)
        
        # Full list compatibility
        isinstance(result, list)  # True
        for obj in result: ...
        result[0], result[:10], len(result)
        
        # Rich metadata
        if result.has_failures:
            for failure in result.failures:
                print(failure.error_message)
    """
    
    def __init__(self, objects=None, **kwargs):
        """Initialize with objects and metadata."""
        super().__init__(objects or [])
        self.failures: List[ObjectFailure] = kwargs.get('failures', [])
        self.batch_info: List[BatchInfo] = kwargs.get('batch_info', [])
        self.total_objects: int = kwargs.get('total_objects', len(self))
        self.start_time: Optional[datetime] = kwargs.get('start_time')
        self.end_time: Optional[datetime] = kwargs.get('end_time')
        self.commit_strategy: Optional[str] = kwargs.get('commit_strategy')
        self.batch_size: Optional[int] = kwargs.get('batch_size')
    
    @property
    def successful_count(self) -> int:
        return len(self)
    
    @property
    def failed_count(self) -> int:
        return len(self.failures)
    
    @property
    def success_rate(self) -> float:
        if self.total_objects == 0:
            return 100.0
        return (self.successful_count / self.total_objects) * 100.0
    
    @property
    def has_failures(self) -> bool:
        return len(self.failures) > 0
    
    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def get_failures_by_error_type(self) -> Dict[str, List[ObjectFailure]]:
        """Group failures by exception type."""
        failures_by_type = {}
        for failure in self.failures:
            error_type = type(failure.error).__name__
            failures_by_type.setdefault(error_type, []).append(failure)
        return failures_by_type
    
    def __repr__(self):
        return (
            f"<BulkCreateResult: {self.successful_count}/{self.total_objects} succeeded, "
            f"{self.failed_count} failed, {len(self.batch_info)} batches>"
        )

