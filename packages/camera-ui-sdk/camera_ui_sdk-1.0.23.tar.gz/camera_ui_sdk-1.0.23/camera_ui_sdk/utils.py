"""Utility functions for the SDK."""

from __future__ import annotations

from typing import Any


def is_equal(first: Any, second: Any, ignore_order: bool = False) -> bool:
    """
    Deep equality check for objects and arrays.

    Used for comparing sensor property values before triggering updates.

    Args:
        first: First value to compare
        second: Second value to compare
        ignore_order: If True, lists are compared ignoring element order

    Returns:
        True if values are deeply equal
    """
    # Same reference or both primitive and equal
    if first is second:
        return True

    # Handle None
    if first is None or second is None:
        return first is second

    # Different types
    if type(first) is not type(second):
        return False

    # List comparison
    if isinstance(first, list):
        if len(first) != len(second):  # pyright: ignore[reportUnknownArgumentType]
            return False
        if ignore_order:
            second_copy = list(second)
            for item in first:  # pyright: ignore[reportUnknownVariableType]
                found = False
                for i, second_item in enumerate(second_copy):
                    if is_equal(item, second_item, ignore_order):
                        second_copy.pop(i)
                        found = True
                        break
                if not found:
                    return False
            return True
        else:
            return all(
                is_equal(item, second[i], ignore_order)
                for i, item in enumerate(first)  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType]
            )

    # Dict comparison
    if isinstance(first, dict):
        if len(first) != len(second):  # pyright: ignore[reportUnknownArgumentType]
            return False
        for key in first:  # pyright: ignore[reportUnknownVariableType]
            if key not in second:
                return False
            if not is_equal(first[key], second[key], ignore_order):
                return False
        return True

    # Primitive comparison (fallback)
    return bool(first == second)
