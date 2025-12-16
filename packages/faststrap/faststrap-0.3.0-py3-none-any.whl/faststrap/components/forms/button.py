"""Bootstrap Button component with variants, sizes, and loading states."""

from typing import Any, Literal

from fasthtml.common import Button as FTButton
from fasthtml.common import I, Span

from ...core.base import merge_classes
from ...utils.attrs import convert_attrs

VariantType = Literal[
    "primary", "secondary", "success", "danger", "warning", "info", "light", "dark", "link"
]
SizeType = Literal["sm", "lg"]


def Button(
    *children: Any,
    variant: VariantType = "primary",
    size: SizeType | None = None,
    outline: bool = False,
    disabled: bool = False,
    loading: bool = False,
    icon: str | None = None,
    **kwargs: Any,
) -> FTButton:
    """Bootstrap Button component.

    Args:
        *children: Button content (text, elements)
        variant: Bootstrap color variant
        size: Button size (sm, lg, or None for default)
        outline: Use outline style
        disabled: Disable button
        loading: Show loading spinner and disable
        icon: Bootstrap icon name (e.g., 'check-circle')
        **kwargs: Additional HTML attributes (cls, id, hx-*, data-*, etc.)

    Returns:
        FastHTML Button element

    Example:
        Basic usage:
        >>> Button("Click Me", variant="primary")

        With icon and HTMX:
        >>> Button("Save", variant="success", icon="check", hx_post="/save")

        Loading state:
        >>> Button("Submitting...", loading=True)
    """
    # Build base classes
    if outline and variant != "link":  # "link" doesn't have outline variant
        classes = [f"btn-outline-{variant}"]
    else:
        classes = [f"btn-{variant}"]

    # Add size class if specified
    if size:
        classes.append(f"btn-{size}")

    # Merge with user classes
    user_cls = kwargs.pop("cls", "")
    all_classes = merge_classes("btn", " ".join(classes), user_cls)

    # Build attributes with proper conversion
    attrs: dict[str, Any] = {"cls": all_classes}

    # Handle disabled/loading states
    if loading or disabled:
        attrs["disabled"] = True

    # Convert remaining kwargs (including hx_*, data_*, etc.)
    attrs.update(convert_attrs(kwargs))

    # Build content
    content = list(children)

    if loading:
        spinner = Span(
            cls="spinner-border spinner-border-sm me-2", role="status", aria_hidden="true"
        )
        content.insert(0, spinner)
    elif icon:
        icon_elem = I(cls=f"bi bi-{icon} me-2", aria_hidden="true")
        content.insert(0, icon_elem)

    return FTButton(*content, **attrs)
