"""
Central registry for hook handlers.

Provides thread-safe registration and lookup of hooks with
deterministic priority ordering.
"""

import logging
import threading
from collections.abc import Callable

from django_bulk_hooks.enums import Priority

logger = logging.getLogger(__name__)

# Type alias for hook info tuple
HookInfo = tuple[type, str, Callable | None, int]


class HookRegistry:
    """
    Central registry for all hook handlers.

    Manages registration, lookup, and lifecycle of hooks with
    thread-safe operations and deterministic ordering by priority.

    This is a singleton - use get_registry() to access the instance.
    """

    def __init__(self):
        """Initialize an empty registry with thread-safe storage."""
        self._hooks: dict[tuple[type, str], list[HookInfo]] = {}
        self._lock = threading.RLock()

    def register(
        self,
        model: type,
        event: str,
        handler_cls: type,
        method_name: str,
        condition: Callable | None,
        priority: int | Priority,
    ) -> None:
        """
        Register a hook handler for a model and event.

        Args:
            model: Django model class
            event: Event name (e.g., 'after_update', 'before_create')
            handler_cls: Hook handler class
            method_name: Name of the method to call on handler
            condition: Optional condition to filter records
            priority: Execution priority (lower values execute first)
        """
        with self._lock:
            key = (model, event)
            hooks = self._hooks.setdefault(key, [])

            # Check for duplicates before adding
            hook_info = (handler_cls, method_name, condition, priority)
            if hook_info not in hooks:
                hooks.append(hook_info)
                # Sort by priority (lower values first)
                hooks.sort(key=lambda x: x[3])
            else:
                pass  # Hook already registered

    def get_hooks(self, model: type, event: str) -> list[HookInfo]:
        """
        Get all hooks for a model and event.

        Args:
            model: Django model class
            event: Event name

        Returns:
            List of hook info tuples (handler_cls, method_name, condition, priority)
            sorted by priority (lower values first)
        """
        with self._lock:
            key = (model, event)
            hooks = self._hooks.get(key, [])
            logger.debug(f"Retrieved {len(hooks)} hooks for {model.__name__}.{event}")
            return hooks

    def get_hooks_including_abstract(self, model: type, event: str) -> list[HookInfo]:
        """
        Get hooks for a concrete model, including hooks registered on abstract bases.

        Args:
            model: Django model class (concrete)
            event: Event name

        Returns:
            Merged list of hook info tuples from the model and its abstract bases,
            sorted by priority (lower values first).
        """
        from django.db import models as dj_models  # lazy import to avoid hard dependency at module load

        with self._lock:
            merged: list[HookInfo] = []

            # Include hooks registered directly on the concrete model
            merged.extend(self._hooks.get((model, event), []))

            # Walk MRO for abstract bases and include their hooks
            for base in model.__mro__[1:]:
                # Only consider Django model classes that are abstract
                if not isinstance(base, type):
                    continue
                if not issubclass(base, dj_models.Model):
                    continue
                if not getattr(getattr(base, "_meta", None), "abstract", False):
                    continue

                merged.extend(self._hooks.get((base, event), []))

            # Sort deterministically by priority
            merged.sort(key=lambda x: x[3])
            logger.debug(f"Retrieved {len(merged)} hooks (incl. abstract) for {model.__name__}.{event}")
            return merged

    def unregister(
        self,
        model: type,
        event: str,
        handler_cls: type,
        method_name: str,
    ) -> None:
        """
        Unregister a specific hook handler.

        Used when child classes override parent hook methods.

        Args:
            model: Django model class
            event: Event name
            handler_cls: Hook handler class to remove
            method_name: Method name to remove
        """
        with self._lock:
            key = (model, event)
            if key not in self._hooks:
                return

            hooks = self._hooks[key]
            # Filter out the specific hook
            self._hooks[key] = [
                (h_cls, m_name, cond, pri) for h_cls, m_name, cond, pri in hooks if not (h_cls == handler_cls and m_name == method_name)
            ]

            # Clean up empty hook lists
            if not self._hooks[key]:
                del self._hooks[key]

    def clear(self) -> None:
        """
        Clear all registered hooks.

        Useful for testing to ensure clean state between tests.
        """
        with self._lock:
            self._hooks.clear()

            # Also clear HookMeta state to ensure complete reset
            from django_bulk_hooks.handler import HookMeta

            HookMeta._registered.clear()
            HookMeta._class_hook_map.clear()

    def list_all(self) -> dict[tuple[type, str], list[HookInfo]]:
        """
        Get all registered hooks for debugging.

        Returns:
            Dictionary mapping (model, event) tuples to lists of hook info
        """
        with self._lock:
            return dict(self._hooks)

    @property
    def hooks(self) -> dict[tuple[type, str], list[HookInfo]]:
        """
        Expose internal hooks dictionary for testing purposes.

        This property provides direct access to the internal hooks storage
        to allow tests to clear the registry state between test runs.
        """
        return self._hooks

    def count_hooks(
        self,
        model: type | None = None,
        event: str | None = None,
    ) -> int:
        """
        Count registered hooks, optionally filtered by model and/or event.

        Args:
            model: Optional model class to filter by
            event: Optional event name to filter by

        Returns:
            Number of matching hooks
        """
        with self._lock:
            if model is None and event is None:
                # Count all hooks
                return sum(len(hooks) for hooks in self._hooks.values())
            if model is not None and event is not None:
                # Count hooks for specific model and event
                return len(self._hooks.get((model, event), []))
            if model is not None:
                # Count all hooks for a model
                return sum(len(hooks) for (m, _), hooks in self._hooks.items() if m == model)
            # event is not None
            # Count all hooks for an event
            return sum(len(hooks) for (_, e), hooks in self._hooks.items() if e == event)


# Global singleton registry
_registry: HookRegistry | None = None
_registry_lock = threading.Lock()


def get_registry() -> HookRegistry:
    """
    Get the global hook registry instance.

    Creates the registry on first access (singleton pattern).
    Thread-safe initialization.

    Returns:
        HookRegistry singleton instance
    """
    global _registry

    if _registry is None:
        with _registry_lock:
            # Double-checked locking
            if _registry is None:
                _registry = HookRegistry()

    return _registry


# Backward-compatible module-level functions
def register_hook(
    model: type,
    event: str,
    handler_cls: type,
    method_name: str,
    condition: Callable | None,
    priority: int | Priority,
) -> None:
    """
    Register a hook handler (backward-compatible function).

    Delegates to the global registry instance.
    """
    registry = get_registry()
    registry.register(model, event, handler_cls, method_name, condition, priority)


def get_hooks(model: type, event: str) -> list[HookInfo]:
    """
    Get hooks for a model and event (backward-compatible function).

    Delegates to the global registry instance.
    """
    registry = get_registry()
    return registry.get_hooks(model, event)


def unregister_hook(
    model: type,
    event: str,
    handler_cls: type,
    method_name: str,
) -> None:
    """
    Unregister a hook handler (backward-compatible function).

    Delegates to the global registry instance.
    """
    registry = get_registry()
    registry.unregister(model, event, handler_cls, method_name)


def clear_hooks() -> None:
    """
    Clear all registered hooks (backward-compatible function).

    Delegates to the global registry instance.
    Useful for testing.
    """
    registry = get_registry()
    registry.clear()


def list_all_hooks() -> dict[tuple[type, str], list[HookInfo]]:
    """
    List all registered hooks (backward-compatible function).

    Delegates to the global registry instance.
    """
    registry = get_registry()
    return registry.list_all()


# Expose hooks dictionary for testing purposes
# This provides backward compatibility with tests that expect to access _hooks directly
_hooks = get_registry().hooks
