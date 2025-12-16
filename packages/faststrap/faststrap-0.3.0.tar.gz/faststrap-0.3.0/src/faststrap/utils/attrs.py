# src/faststrap/utils/attrs.py
"""Attribute conversion utilities."""

from typing import Any


def convert_attrs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Convert Python kwargs to HTML attributes (hx_get → hx-get).

    Handles:
    - HTMX attributes (hx_*)
    - Data attributes (data_*)
    - ARIA attributes (aria_*)
    - All other attributes with underscores

    Args:
        kwargs: Python-style keyword arguments

    Returns:
        HTML-style attributes with hyphens

    Example:
        >>> convert_attrs({"hx_get": "/api", "data_value": "123"})
        {"hx-get": "/api", "data-value": "123"}
    """
    converted = {}
    for k, v in kwargs.items():
        # Keep cls as-is (FastHTML convention)
        if k == "cls":
            converted[k] = v
        # Convert underscore to hyphen for all other attributes
        else:
            converted[k.replace("_", "-")] = v

    return converted
