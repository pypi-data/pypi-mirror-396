"""Settings for django-bulk-hooks."""
from django.conf import settings


DEFAULTS = {
    'BATCH_SIZES': {
        'create': {'default': 500, 'large_dataset': 200, 'huge_dataset': 100, 'minimum': 10},
        'update': {'default': 1000, 'large_dataset': 500, 'huge_dataset': 250, 'minimum': 10},
        'thresholds': {'large': 10_000, 'huge': 50_000},
    },
    'LIMITS': {'max_objects_per_operation': 500_000, 'max_batches_per_operation': 1000},
    'ERROR_HANDLING': {'max_failure_rate_percent': 10.0, 'fail_fast': True},
    'MONITORING': {'log_batch_progress': True, 'log_timing_info': True},
}


def get_setting(setting_name, default=None):
    """Get setting from Django settings."""
    bulk_hooks_settings = getattr(settings, 'BULK_HOOKS', {})
    if default is None:
        default = DEFAULTS.get(setting_name)
    return bulk_hooks_settings.get(setting_name, default)


def calculate_batch_size(operation_type: str, object_count: int, user_batch_size=None) -> int:
    """
    Calculate optimal batch size with validation.
    
    Validates minimum and handles edge cases.
    """
    batch_sizes = get_setting('BATCH_SIZES')
    op_config = batch_sizes.get(operation_type, batch_sizes['create'])
    minimum = op_config.get('minimum', 10)
    
    if user_batch_size is not None:
        if user_batch_size < minimum:
            raise ValueError(f"batch_size must be at least {minimum}, got {user_batch_size}")
        # Handle case where batch_size > object_count
        if user_batch_size > object_count:
            return object_count
        return user_batch_size
    
    thresholds = batch_sizes['thresholds']
    if object_count > thresholds['huge']:
        return max(op_config['huge_dataset'], minimum)
    elif object_count > thresholds['large']:
        return max(op_config['large_dataset'], minimum)
    return max(op_config['default'], minimum)

