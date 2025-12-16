"""
Model analyzer service - Combines validation and field tracking.

This service handles all model analysis needs:
- Input validation
- Field change detection
- Field comparison
- Expression resolution
"""

import logging
from typing import Any, Dict, List, Optional, Set

from django.db.models import Expression, Model
from django.db.models.expressions import Combinable

from django_bulk_hooks.helpers import extract_pks

from .field_utils import get_auto_fields, get_changed_fields, get_fk_fields

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class ModelAnalyzer:
    """
    Analyzes models and validates operations.

    This service combines validation and field tracking responsibilities
    since they're closely related and often used together.

    Design Principles:
    - Single source of truth for data fetching
    - Bulk operations to prevent N+1 queries
    - Clear separation between validation and analysis
    """

    # Validation requirements per operation type
    VALIDATION_REQUIREMENTS = {
        "bulk_create": ["types"],
        "bulk_update": ["types", "has_pks"],
        "delete": ["types"],
    }

    def __init__(self, model_cls: type):
        """
        Initialize analyzer for a specific model.

        Args:
            model_cls: The Django model class to analyze
        """
        self.model_cls = model_cls

    # ==================== PUBLIC VALIDATION API ====================

    def validate_for_create(self, objs: List[Model]) -> bool:
        """
        Validate objects for bulk_create operation.

        Args:
            objs: List of model instances

        Returns:
            True if validation passes

        Raises:
            TypeError: If objects are not instances of model_cls
        """
        return self.validate_for_operation(objs, "bulk_create")

    def validate_for_update(self, objs: List[Model]) -> bool:
        """
        Validate objects for bulk_update operation.

        Args:
            objs: List of model instances

        Returns:
            True if validation passes

        Raises:
            TypeError: If objects are not instances of model_cls
            ValueError: If objects don't have primary keys
        """
        return self.validate_for_operation(objs, "bulk_update")

    def validate_for_delete(self, objs: List[Model]) -> bool:
        """
        Validate objects for delete operation.

        Args:
            objs: List of model instances

        Returns:
            True if validation passes

        Raises:
            TypeError: If objects are not instances of model_cls
        """
        return self.validate_for_operation(objs, "delete")

    def validate_for_operation(self, objs: List[Model], operation: str) -> bool:
        """
        Centralized validation method that applies operation-specific checks.

        This method routes to appropriate validation checks based on the
        operation type, ensuring consistent validation across all operations.

        Args:
            objs: List of model instances to validate
            operation: String identifier for the operation

        Returns:
            True if validation passes

        Raises:
            TypeError: If type validation fails
            ValueError: If PK validation fails
        """
        requirements = self.VALIDATION_REQUIREMENTS.get(operation, [])

        if "types" in requirements:
            self._validate_types(objs, operation)

        if "has_pks" in requirements:
            self._validate_has_pks(objs, operation)

        return True

    # ==================== DATA FETCHING ====================

    def fetch_old_records_map(self, instances: List[Model]) -> Dict[Any, Model]:
        """
        Fetch old records for instances in a single bulk query.

        This is the SINGLE source of truth for fetching old records.
        All other methods should delegate to this to ensure consistency
        and prevent duplicate queries.

        Performance: O(1) queries regardless of number of instances.

        Args:
            instances: List of model instances

        Returns:
            Dict mapping pk -> old instance for O(1) lookups
        """
        pks = extract_pks(instances)
        if not pks:
            return {}

        old_records = self.model_cls._base_manager.filter(pk__in=pks)
        return {obj.pk: obj for obj in old_records}

    # ==================== FIELD INTROSPECTION ====================

    def get_auto_now_fields(self) -> List[str]:
        """
        Get fields that have auto_now or auto_now_add set.

        These fields are automatically updated by Django and should
        typically be excluded from manual change tracking.

        Returns:
            List of field names with auto_now behavior
        """
        return get_auto_fields(self.model_cls, include_auto_now_add=True)

    def get_fk_fields(self) -> List[str]:
        """
        Get all foreign key fields for the model.

        Returns:
            List of FK field names
        """
        return get_fk_fields(self.model_cls)

    def detect_changed_fields(self, objs: List[Model]) -> List[str]:
        """
        Detect which fields have changed across a set of objects.

        This method fetches old records from the database in a SINGLE bulk query
        and compares them with the new objects to determine changed fields.

        Performance: Uses bulk query (O(1) queries) not N queries.

        Args:
            objs: List of model instances to check

        Returns:
            Sorted list of field names that changed across any object
        """
        if not objs:
            return []

        # Fetch old records using single source of truth
        old_records_map = self.fetch_old_records_map(objs)
        if not old_records_map:
            return []

        # Collect all changed fields across objects
        changed_fields_set: Set[str] = set()

        for obj in objs:
            if obj.pk is None:
                continue

            old_obj = old_records_map.get(obj.pk)
            if old_obj is None:
                continue

            # Use canonical field comparison (skips auto_created fields)
            changed_fields = get_changed_fields(old_obj, obj, self.model_cls, skip_auto_fields=True)
            changed_fields_set.update(changed_fields)

        # Return sorted list for deterministic behavior
        return sorted(changed_fields_set)

    # ==================== EXPRESSION RESOLUTION ====================

    def resolve_expression(self, field_name: str, expression: Any, instance: Model) -> Any:
        """
        Resolve a SQL expression to a concrete value for a specific instance.

        This method materializes database expressions (F(), Subquery, Case, etc.)
        into concrete values by using Django's annotate() mechanism.

        Args:
            field_name: Name of the field being updated
            expression: The expression or value to resolve
            instance: The model instance to resolve for

        Returns:
            The resolved concrete value, or original expression if resolution fails
        """
        # Simple value - return as-is
        if not self._is_expression(expression):
            return expression

        # Complex expression - resolve in database context
        try:
            return self._resolve_expression_for_instance(field_name, expression, instance)
        except Exception as e:
            logger.warning(
                "Failed to resolve expression for field '%s' on %s: %s. Using original value.", field_name, self.model_cls.__name__, e
            )
            return expression

    def apply_update_values(self, instances: List[Model], update_kwargs: Dict[str, Any]) -> List[str]:
        """
        Apply update_kwargs to instances, resolving any SQL expressions.

        This method transforms queryset.update()-style kwargs (which may contain
        F() expressions, Subquery, Case, etc.) into concrete values and applies
        them to the instances.

        Performance: Resolves complex expressions in bulk queries where possible.

        Args:
            instances: List of model instances to update
            update_kwargs: Dict of {field_name: value_or_expression}

        Returns:
            List of field names that were updated
        """
        if not instances or not update_kwargs:
            return []

        fields_updated = list(update_kwargs.keys())

        # Get instances with PKs
        instances_with_pks = [inst for inst in instances if inst.pk is not None]
        if not instances_with_pks:
            return fields_updated

        # Process each field
        for field_name, value in update_kwargs.items():
            if self._is_expression(value):
                self._apply_expression_value(field_name, value, instances_with_pks)
            else:
                self._apply_simple_value(field_name, value, instances)

        return fields_updated

    # ==================== PRIVATE VALIDATION METHODS ====================

    def _validate_types(self, objs: List[Model], operation: str = "operation") -> None:
        """
        Validate that all objects are instances of the model class.

        Args:
            objs: List of objects to validate
            operation: Name of the operation (for error messages)

        Raises:
            TypeError: If any object is not an instance of model_cls
        """
        if not objs:
            return

        invalid_types = {type(obj).__name__ for obj in objs if not isinstance(obj, self.model_cls)}

        if invalid_types:
            raise TypeError(f"{operation} expected instances of {self.model_cls.__name__}, but got {invalid_types}")

    def _validate_has_pks(self, objs: List[Model], operation: str = "operation") -> None:
        """
        Validate that all objects have primary keys.

        Args:
            objs: List of objects to validate
            operation: Name of the operation (for error messages)

        Raises:
            ValueError: If any object is missing a primary key
        """
        missing_pks = [obj for obj in objs if obj.pk is None]

        if missing_pks:
            raise ValueError(
                f"{operation} cannot operate on unsaved {self.model_cls.__name__} "
                f"instances. {len(missing_pks)} object(s) have no primary key."
            )

    # ==================== PRIVATE EXPRESSION METHODS ====================

    def _is_expression(self, value: Any) -> bool:
        """
        Check if a value is a Django database expression.

        Args:
            value: Value to check

        Returns:
            True if value is an Expression or Combinable
        """
        return isinstance(value, (Expression, Combinable))

    def _resolve_expression_for_instance(self, field_name: str, expression: Any, instance: Model) -> Any:
        """
        Resolve an expression for a single instance using database query.

        Args:
            field_name: Field name being resolved
            expression: Django expression to resolve
            instance: Model instance to resolve for

        Returns:
            Resolved concrete value

        Raises:
            Exception: If expression cannot be resolved
        """
        instance_qs = self.model_cls.objects.filter(pk=instance.pk)

        resolved_value = instance_qs.annotate(_resolved_value=expression).values_list("_resolved_value", flat=True).first()

        return resolved_value

    def _apply_simple_value(self, field_name: str, value: Any, instances: List[Model]) -> None:
        """
        Apply a simple (non-expression) value to all instances.

        Args:
            field_name: Name of field to update
            value: Simple value to apply
            instances: List of instances to update
        """
        for instance in instances:
            setattr(instance, field_name, value)

    def _apply_expression_value(self, field_name: str, expression: Any, instances: List[Model]) -> None:
        """
        Resolve and apply an expression value to all instances in bulk.

        This method resolves the expression for all instances in a single
        database query for optimal performance.

        Args:
            field_name: Name of field to update
            expression: Django expression to resolve
            instances: List of instances to update
        """
        try:
            # Resolve expression for all instances in single query
            value_map = self._bulk_resolve_expression(expression, instances)

            # Apply resolved values to instances
            for instance in instances:
                if instance.pk in value_map:
                    setattr(instance, field_name, value_map[instance.pk])

        except Exception as e:
            logger.warning(
                "Failed to resolve expression for field '%s' on %s: %s. Using original value.", field_name, self.model_cls.__name__, e
            )
            # Fallback: apply original expression value
            self._apply_simple_value(field_name, expression, instances)

    def _bulk_resolve_expression(self, expression: Any, instances: List[Model]) -> Dict[Any, Any]:
        """
        Resolve an expression for multiple instances in a single query.

        Args:
            expression: Django expression to resolve
            instances: List of instances to resolve for

        Returns:
            Dict mapping pk -> resolved value

        Raises:
            Exception: If expression cannot be resolved
        """
        pks = extract_pks(instances)
        if not pks:
            return {}

        # Query all instances with annotated expression
        qs = self.model_cls.objects.filter(pk__in=pks)
        results = qs.annotate(_resolved_value=expression).values_list("pk", "_resolved_value")

        return dict(results)


# ==================== CONVENIENCE FUNCTIONS ====================


def create_analyzer(model_cls: type) -> ModelAnalyzer:
    """
    Factory function to create a ModelAnalyzer instance.

    This provides a convenient entry point and allows for future
    extensibility (e.g., analyzer caching, subclass selection).

    Args:
        model_cls: The Django model class to analyze

    Returns:
        ModelAnalyzer instance for the model
    """
    return ModelAnalyzer(model_cls)


def validate_instances(instances: List[Model], model_cls: type, operation: str) -> bool:
    """
    Convenience function to validate instances for an operation.

    Args:
        instances: List of model instances to validate
        model_cls: Expected model class
        operation: Operation type ('bulk_create', 'bulk_update', 'delete')

    Returns:
        True if validation passes

    Raises:
        TypeError: If type validation fails
        ValueError: If PK validation fails
    """
    analyzer = create_analyzer(model_cls)
    return analyzer.validate_for_operation(instances, operation)
