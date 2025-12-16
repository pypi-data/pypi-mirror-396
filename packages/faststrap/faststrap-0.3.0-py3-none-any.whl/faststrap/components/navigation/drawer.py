"""Bootstrap Offcanvas (Drawer) component for side panels."""

from typing import Any, Literal

from fasthtml.common import H5, Button, Div

from ...core.base import merge_classes
from ...utils.attrs import convert_attrs

PlacementType = Literal["start", "end", "top", "bottom"]


# @register(category="feedback", requires_js=True)
def Drawer(
    *children: Any,
    drawer_id: str,  # Using drawer_id to avoid conflict
    title: str | None = None,
    placement: PlacementType = "start",
    backdrop: bool = True,
    scroll: bool = False,
    dark: bool = False,
    **kwargs: Any,
) -> Div:
    """Bootstrap Offcanvas (Drawer) component for side panels and menus.

    Args:
        *children: Drawer body content
        drawer_id: Unique ID for the drawer (required for Bootstrap JS)
        title: Drawer header title
        placement: Drawer position (start=left, end=right, top, bottom)
        backdrop: Show backdrop overlay (default: True)
        scroll: Allow body scroll when drawer is open (default: False)
        **kwargs: Additional HTML attributes (cls, hx-*, data-*, etc.)

    Returns:
        FastHTML Div element with offcanvas structure

    Example:
        Left sidebar drawer:
        >>> Drawer(
        ...     Nav(
        ...         A("Home", href="/"),
        ...         A("About", href="/about"),
        ...         A("Contact", href="/contact")
        ...     ),
        ...     drawer_id="sidebar",
        ...     title="Menu",
        ...     placement="start"
        ... )

        Right drawer:
        >>> Drawer(
        ...     "Notifications here",
        ...     drawer_id="notifications",
        ...     title="Alerts",
        ...     placement="end"
        ... )

        No backdrop (allows interaction with page):
        >>> Drawer(
        ...     "Settings",
        ...     drawer_id="settings",
        ...     title="Settings",
        ...     backdrop=False,
        ...     scroll=True
        ... )

        Top drawer (full-width):
        >>> Drawer(
        ...     "Search results",
        ...     drawer_id="search",
        ...     title="Search",
        ...     placement="top"
        ... )

    Note:
        To trigger a drawer, use Bootstrap's data attributes:
        >>> Button("Open Menu", data_bs_toggle="offcanvas", data_bs_target="#sidebar")

        Or use HTMX to load drawer content dynamically:
        >>> Button("Load Drawer", hx_get="/drawer-content", hx_target="#drawerContainer")

    See Also:
        Bootstrap docs: https://getbootstrap.com/docs/5.3/components/offcanvas/
    """
    # Build offcanvas classes
    classes = ["offcanvas", f"offcanvas-{placement}"]

    if dark:  # ← Bootstrap 5.3+ dark variant
        classes.append("offcanvas-dark")

    # Merge with user classes
    user_cls = kwargs.pop("cls", "")
    all_classes = merge_classes(" ".join(classes), user_cls)

    # Build attributes (WITHOUT id - we'll add it later)
    attrs: dict[str, Any] = {
        "cls": all_classes,
        "tabindex": "-1",
        "aria_labelledby": f"{drawer_id}Label",
    }

    # Configure backdrop and scroll
    if not backdrop:
        attrs["data_bs_backdrop"] = "false"

    if scroll:
        attrs["data_bs_scroll"] = "true"

    # Convert remaining kwargs (excluding drawer_id)
    converted_kwargs = convert_attrs({k: v for k, v in kwargs.items() if k != "drawer_id"})
    attrs.update(converted_kwargs)

    # Build drawer structure
    parts = []

    # Header
    if title:
        header = Div(
            H5(title, cls="offcanvas-title", id=f"{drawer_id}Label"),
            Button(
                type="button",
                cls="btn-close",
                data_bs_dismiss="offcanvas",
                aria_label="Close",
            ),
            cls="offcanvas-header",
        )
        parts.append(header)

    # Body
    body = Div(*children, cls="offcanvas-body")
    parts.append(body)

    # Create the drawer with correct attrs including id
    return Div(*parts, id=drawer_id, **attrs)
