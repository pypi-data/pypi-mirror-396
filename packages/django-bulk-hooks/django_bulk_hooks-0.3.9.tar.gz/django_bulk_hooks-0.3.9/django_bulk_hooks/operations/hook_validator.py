"""Hook compatibility validation."""
import logging

logger = logging.getLogger(__name__)


# Based on actual codebase conditions
BATCH_INCOMPATIBLE_CONDITIONS = {
    'HasChanged',  # Compares to old values
    'WasEqual',    # Checks previous state
    'ChangesTo',   # Checks state transitions
}


def _check_condition_recursive(condition, handler_cls, method_name, event, incompatible):
    """
    Recursively check condition tree.
    
    Handles actual codebase structure:
    - AndCondition/OrCondition: .cond1 and .cond2
    - NotCondition: .cond
    """
    if condition is None:
        return
    
    condition_type = type(condition).__name__
    if condition_type in BATCH_INCOMPATIBLE_CONDITIONS:
        incompatible.append(
            f"{handler_cls.__name__}.{method_name} ({event}) uses {condition_type}"
        )
    
    # AndCondition and OrCondition
    if hasattr(condition, 'cond1') and hasattr(condition, 'cond2'):
        _check_condition_recursive(condition.cond1, handler_cls, method_name, event, incompatible)
        _check_condition_recursive(condition.cond2, handler_cls, method_name, event, incompatible)
    
    # NotCondition
    if hasattr(condition, 'cond'):
        _check_condition_recursive(condition.cond, handler_cls, method_name, event, incompatible)


def check_hook_compatibility(registry, model_cls: type, operation: str, commit_strategy) -> list:
    """Check if hooks are compatible."""
    from django_bulk_hooks.enums import CommitStrategy
    
    if commit_strategy == CommitStrategy.ATOMIC:
        return []
    
    incompatible = []
    events = [f'validate_{operation}', f'before_{operation}', f'after_{operation}']
    
    for event in events:
        hooks = registry.get_hooks(model_cls, event)
        for handler_cls, method_name, condition, priority in hooks:
            _check_condition_recursive(condition, handler_cls, method_name, event, incompatible)
    
    return incompatible


def validate_hook_compatibility_or_raise(registry, model_cls: type, operation: str, commit_strategy) -> None:
    """Validate and raise ValueError if incompatible."""
    incompatible = check_hook_compatibility(registry, model_cls, operation, commit_strategy)
    
    if incompatible:
        error_msg = (
            f"Cannot use commit_strategy={commit_strategy.value} with {model_cls.__name__} "
            f"due to incompatible hooks:\n"
        )
        for issue in incompatible:
            error_msg += f"  - {issue}\n"
        error_msg += (
            "\nBatch modes cause hooks to see only the current batch.\n\n"
            "Solutions:\n"
            "  1. Use commit_strategy=CommitStrategy.ATOMIC (default)\n"
            "  2. Remove or modify incompatible hooks\n"
            "  3. Process batches manually"
        )
        raise ValueError(error_msg)

