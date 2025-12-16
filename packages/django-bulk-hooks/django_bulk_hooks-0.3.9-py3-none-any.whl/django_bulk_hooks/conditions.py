import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=512)
def _get_field_metadata(model_cls, field_name):
    """
    Get cached field metadata for a model and field name.

    Returns:
        Tuple of (field, is_relation, attname) or (None, False, None) if not found
    """
    try:
        field = model_cls._meta.get_field(field_name)
        is_relation = field.is_relation and not field.many_to_many
        attname = field.attname if is_relation else field_name
        return (field, is_relation, attname)
    except Exception:
        return (None, False, None)


def resolve_field_path(instance, field_path):
    """
    Recursively resolve a field path using Django's __ notation, e.g., "author__profile__name".

    CRITICAL: For foreign key fields, uses attname to access the ID directly
    to avoid hooking Django's descriptor protocol which causes N+1 queries.
    """
    # For simple field access (no __), use optimized field access
    if "__" not in field_path:
        # Use cached field metadata lookup
        model_cls = instance.__class__
        field, is_relation, attname = _get_field_metadata(model_cls, field_path)

        if field is not None:
            if is_relation:
                # For foreign key fields, use attname to get the ID directly
                # This avoids hooking Django's descriptor protocol
                return getattr(instance, attname, None)
            # For regular fields, use normal getattr
            return getattr(instance, field_path, None)
        else:
            # If field lookup fails, fall back to normal getattr
            return getattr(instance, field_path, None)

    # For paths with __, traverse the relationship chain with FK optimization
    current_instance = instance
    attrs = field_path.split("__")
    for i, attr in enumerate(attrs):
        if current_instance is None:
            return None

        try:
            # Check if this is the last attribute and if it's a FK field
            is_last_attr = i == len(attrs) - 1
            if is_last_attr and hasattr(current_instance, "_meta"):
                # Use cached field metadata lookup
                model_cls = current_instance.__class__
                field, is_relation, attname = _get_field_metadata(model_cls, attr)

                if field is not None and is_relation:
                    # Use attname for the final FK field access
                    current_instance = getattr(current_instance, attname, None)
                    continue

            # Normal getattr for non-FK fields or when FK optimization not applicable
            current_instance = getattr(current_instance, attr, None)
        except Exception:
            current_instance = None

    return current_instance


class HookCondition:
    def check(self, instance, original_instance=None, changeset=None):
        raise NotImplementedError

    def __call__(self, instance, original_instance=None, changeset=None):
        try:
            return self.check(instance, original_instance, changeset)
        except TypeError:
            # Backward-compatible: allow conditions without changeset param
            return self.check(instance, original_instance)

    def __and__(self, other):
        return AndCondition(self, other)

    def __or__(self, other):
        return OrCondition(self, other)

    def __invert__(self):
        return NotCondition(self)


class IsNotEqual(HookCondition):
    def __init__(self, field, value, only_on_change=False):
        self.field = field
        self.value = value
        self.only_on_change = only_on_change

    def check(self, instance, original_instance=None):
        current = resolve_field_path(instance, self.field)
        if self.only_on_change:
            if original_instance is None:
                return False
            previous = resolve_field_path(original_instance, self.field)
            return previous == self.value and current != self.value
        return current != self.value


class IsEqual(HookCondition):
    def __init__(self, field, value, only_on_change=False):
        self.field = field
        self.value = value
        self.only_on_change = only_on_change

    def check(self, instance, original_instance=None):
        current = resolve_field_path(instance, self.field)

        if self.only_on_change:
            if original_instance is None:
                return False
            previous = resolve_field_path(original_instance, self.field)
            return previous != self.value and current == self.value
        return current == self.value


class HasChanged(HookCondition):
    def __init__(self, field, has_changed=True):
        self.field = field
        self.has_changed = has_changed

    def check(self, instance, original_instance=None, changeset=None):
        if not original_instance:
            logger.debug(f"HasChanged({self.field}): No original_instance provided, returning False")
            return False

        current = resolve_field_path(instance, self.field)
        previous = resolve_field_path(original_instance, self.field)

        result = (current != previous) == self.has_changed

        # DEBUG: Log the comparison
        logger.debug(
            f"HasChanged({self.field}): current={current}, previous={previous}, "
            f"changed={current != previous}, expected_changed={self.has_changed}, result={result}"
        )

        # DEBUG: For FK fields, also check __dict__
        if self.field.endswith("_id"):
            current_dict = instance.__dict__.get(self.field)
            previous_dict = original_instance.__dict__.get(self.field) if original_instance else None
            logger.debug(f"HasChanged({self.field}): __dict__ values: current.__dict__={current_dict}, previous.__dict__={previous_dict}")

        return result


class WasEqual(HookCondition):
    def __init__(self, field, value, only_on_change=False):
        """
        Check if a field's original value was `value`.
        If only_on_change is True, only return True when the field has changed away from that value.
        """
        self.field = field
        self.value = value
        self.only_on_change = only_on_change

    def check(self, instance, original_instance=None):
        if original_instance is None:
            return False
        previous = resolve_field_path(original_instance, self.field)
        if self.only_on_change:
            current = resolve_field_path(instance, self.field)
            return previous == self.value and current != self.value
        return previous == self.value


class ChangesTo(HookCondition):
    def __init__(self, field, value):
        """
        Check if a field's value has changed to `value`.
        Only returns True when original value != value and current value == value.
        """
        self.field = field
        self.value = value

    def check(self, instance, original_instance=None):
        if original_instance is None:
            return False
        previous = resolve_field_path(original_instance, self.field)
        current = resolve_field_path(instance, self.field)
        return previous != self.value and current == self.value


class IsGreaterThan(HookCondition):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def check(self, instance, original_instance=None):
        current = resolve_field_path(instance, self.field)
        return current is not None and current > self.value


class IsGreaterThanOrEqual(HookCondition):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def check(self, instance, original_instance=None):
        current = resolve_field_path(instance, self.field)
        return current is not None and current >= self.value


class IsLessThan(HookCondition):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def check(self, instance, original_instance=None):
        current = resolve_field_path(instance, self.field)
        return current is not None and current < self.value


class IsLessThanOrEqual(HookCondition):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def check(self, instance, original_instance=None):
        current = resolve_field_path(instance, self.field)
        return current is not None and current <= self.value


class AndCondition(HookCondition):
    def __init__(self, cond1, cond2):
        self.cond1 = cond1
        self.cond2 = cond2

    def check(self, instance, original_instance=None, changeset=None):
        # Evaluate left condition with adaptive signature
        try:
            left = self.cond1.check(instance, original_instance, changeset)
        except TypeError:
            left = self.cond1.check(instance, original_instance)

        if not left:
            return False

        # Evaluate right condition with adaptive signature
        try:
            right = self.cond2.check(instance, original_instance, changeset)
        except TypeError:
            right = self.cond2.check(instance, original_instance)

        return right


class OrCondition(HookCondition):
    def __init__(self, cond1, cond2):
        self.cond1 = cond1
        self.cond2 = cond2

    def check(self, instance, original_instance=None, changeset=None):
        # Evaluate left condition with adaptive signature
        try:
            left = self.cond1.check(instance, original_instance, changeset)
        except TypeError:
            left = self.cond1.check(instance, original_instance)

        if left:
            return True

        # Evaluate right condition with adaptive signature
        try:
            right = self.cond2.check(instance, original_instance, changeset)
        except TypeError:
            right = self.cond2.check(instance, original_instance)

        return right


class NotCondition(HookCondition):
    def __init__(self, cond):
        self.cond = cond

    def check(self, instance, original_instance=None, changeset=None):
        try:
            result = self.cond.check(instance, original_instance, changeset)
        except TypeError:
            result = self.cond.check(instance, original_instance)
        return not result
