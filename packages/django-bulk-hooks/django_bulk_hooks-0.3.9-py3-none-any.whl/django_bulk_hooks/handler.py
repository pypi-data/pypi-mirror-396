import logging

from django_bulk_hooks.registry import register_hook

logger = logging.getLogger(__name__)


class HookMeta(type):
    _registered = set()
    _class_hook_map: dict[
        type,
        set[tuple],
    ] = {}  # Track which hooks belong to which class

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        mcs._register_hooks_for_class(cls)
        return cls

    @classmethod
    def _register_hooks_for_class(mcs, cls):
        """
        Register hooks for a given class following OOP inheritance semantics.

        - Child classes inherit all parent hook methods
        - Child overrides replace parent implementations (not add to them)
        - Child can add new hook methods
        """
        from django_bulk_hooks.registry import unregister_hook

        # Step 1: Unregister ALL hooks from parent classes in the MRO
        # This ensures only the most-derived class owns the active hooks,
        # providing true OOP semantics (overrides replace, others are inherited once).
        for base in cls.__mro__[1:]:  # Skip cls itself, start from first parent
            if not isinstance(base, HookMeta):
                continue

            if base in mcs._class_hook_map:
                for model_cls, event, base_cls, method_name in list(
                    mcs._class_hook_map[base],
                ):
                    key = (model_cls, event, base_cls, method_name)
                    if key in HookMeta._registered:
                        unregister_hook(model_cls, event, base_cls, method_name)
                        HookMeta._registered.discard(key)

        # Step 2: Register all hook methods on this class (including inherited ones)
        # Walk the MRO to find ALL methods with hook decorators
        all_hook_methods = {}
        for klass in reversed(cls.__mro__):  # Start from most base class
            if not isinstance(klass, HookMeta):
                continue
            for method_name, method in klass.__dict__.items():
                if hasattr(method, "hooks_hooks"):
                    # Store with method name as key - child methods will override parent
                    all_hook_methods[method_name] = method

        # Step 3: Register all hook methods with THIS class as the handler
        if cls not in mcs._class_hook_map:
            mcs._class_hook_map[cls] = set()

        for method_name, method in all_hook_methods.items():
            if hasattr(method, "hooks_hooks"):
                for model_cls, event, condition, priority in method.hooks_hooks:
                    key = (model_cls, event, cls, method_name)
                    if key not in HookMeta._registered:
                        register_hook(
                            model=model_cls,
                            event=event,
                            handler_cls=cls,
                            method_name=method_name,
                            condition=condition,
                            priority=priority,
                        )
                        HookMeta._registered.add(key)
                        mcs._class_hook_map[cls].add(key)

    @classmethod
    def re_register_all_hooks(mcs):
        """Re-register all hooks for all existing Hook classes."""
        # Clear the registered set and class hook map so we can re-register
        HookMeta._registered.clear()
        mcs._class_hook_map.clear()

        # Find all Hook classes and re-register their hooks
        import gc

        registered_classes = set()
        for obj in gc.get_objects():
            if isinstance(obj, type) and isinstance(obj, HookMeta):
                if obj not in registered_classes:
                    registered_classes.add(obj)
                    mcs._register_hooks_for_class(obj)


class Hook(metaclass=HookMeta):
    """
    Base class for hook handlers.

    Hooks are registered via the @hook decorator and executed by
    the HookDispatcher. This class serves as a base for all hook
    handlers and uses HookMeta for automatic registration.

    All hook execution logic has been moved to HookDispatcher for
    a single, consistent execution path.
    """
