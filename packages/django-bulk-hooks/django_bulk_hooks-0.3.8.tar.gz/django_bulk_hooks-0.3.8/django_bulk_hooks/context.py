"""
Thread-local context management for bulk operations.

This module provides thread-safe storage for operation state like
bypass_hooks flags and bulk update metadata.
"""

import threading

_hook_context = threading.local()


def set_bypass_hooks(bypass_hooks):
    """Set the current bypass_hooks state for the current thread."""
    _hook_context.bypass_hooks = bypass_hooks


def get_bypass_hooks():
    """Get the current bypass_hooks state for the current thread."""
    return getattr(_hook_context, "bypass_hooks", False)


# Thread-local storage for passing per-object field values from bulk_update -> update
def set_bulk_update_value_map(value_map):
    """Store a mapping of {pk: {field_name: value}} for the current thread.

    This allows the internal update() call (hooked by Django's bulk_update)
    to populate in-memory instances with the concrete values that will be
    written to the database, instead of Django expression objects like Case/Cast.
    """
    _hook_context.bulk_update_value_map = value_map


def get_bulk_update_value_map():
    """Retrieve the mapping {pk: {field_name: value}} for the current thread, if any."""
    return getattr(_hook_context, "bulk_update_value_map", None)


def set_bulk_update_active(active):
    """Set whether we're currently in a bulk_update operation."""
    _hook_context.bulk_update_active = active


def get_bulk_update_active():
    """Get whether we're currently in a bulk_update operation."""
    return getattr(_hook_context, "bulk_update_active", False)


def set_bulk_update_batch_size(batch_size):
    """Store the batch_size for the current bulk_update operation."""
    _hook_context.bulk_update_batch_size = batch_size


def get_bulk_update_batch_size():
    """Get the batch_size for the current bulk_update operation."""
    return getattr(_hook_context, "bulk_update_batch_size", None)
