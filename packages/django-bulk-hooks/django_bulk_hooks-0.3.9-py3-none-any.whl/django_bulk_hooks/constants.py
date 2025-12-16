BEFORE_CREATE = "before_create"
AFTER_CREATE = "after_create"
BEFORE_UPDATE = "before_update"
AFTER_UPDATE = "after_update"
BEFORE_DELETE = "before_delete"
AFTER_DELETE = "after_delete"
VALIDATE_CREATE = "validate_create"
VALIDATE_UPDATE = "validate_update"
VALIDATE_DELETE = "validate_delete"

# Default batch sizes (overridable via BULK_HOOKS Django setting)
DEFAULT_BULK_CREATE_BATCH_SIZE = 500
DEFAULT_BULK_UPDATE_BATCH_SIZE = 1000

# For configurable batch sizing and limits, use BULK_HOOKS settings.
# See django_bulk_hooks.settings for configuration options.
# Example in settings.py:
#   BULK_HOOKS = {
#       'BATCH_SIZES': {...},
#       'LIMITS': {...},
#   }
