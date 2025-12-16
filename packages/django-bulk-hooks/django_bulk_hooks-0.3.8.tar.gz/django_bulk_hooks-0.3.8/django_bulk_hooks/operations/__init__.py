"""
Operations module for django-bulk-hooks.

This module contains all services for bulk operations following
a clean, service-based architecture.
"""

from django_bulk_hooks.operations.analyzer import ModelAnalyzer
from django_bulk_hooks.operations.bulk_executor import BulkExecutor
from django_bulk_hooks.operations.coordinator import BulkOperationCoordinator

__all__ = [
    "BulkExecutor",
    "BulkOperationCoordinator",
    "ModelAnalyzer",
]
