"""
Carbon Design System Icons - Server-Side SVG Rendering

Reads SVG files from CARBON_ICONS_PATH and renders them directly in templates.
No JavaScript, no CDN, no placeholders - just pure SVG markup.

Configuration:
    1. Set CARBON_ICONS_PATH in your Django settings to a directory path
    2. Run: python manage.py fetch_carbon_assets icons
    3. Use in templates: {% carbon_icon "edit" 16 slot="icon" %}

Usage in template:
    {% carbon_icon "edit" 16 slot="icon" %}
"""

import logging
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


@lru_cache(maxsize=256)
def read_carbon_icon_svg(name: str, viewbox: int = 32) -> str:
    """
    Read Carbon icon SVG from CARBON_ICONS_PATH.
    """
    try:
        icons_path = settings.CARBON_ICONS_PATH
    except AttributeError:
        raise ImproperlyConfigured(
            "CARBON_ICONS_PATH is not set in Django settings. "
            "Add CARBON_ICONS_PATH to your settings, then run: "
            "python manage.py fetch_carbon_assets icons"
        ) from None

    icons_path = Path(icons_path)
    if not icons_path.exists():
        raise ImproperlyConfigured(
            f"CARBON_ICONS_PATH points to non-existent directory: {icons_path}\n"
            f"Run: python manage.py fetch_carbon_assets icons"
        )

    # Try to find the icon file
    icon_file = icons_path / str(viewbox) / f"{name}.svg"
    if not icon_file.exists():
        logger.warning(f'CARBON ICON MISSING: "{name}" viewbox={viewbox} at {icon_file}')
        return ""

    return icon_file.read_text()


def render_carbon_icon_svg(name: str, size: int = 16, viewbox: int = 32, **attrs) -> str:
    """
    Render Carbon icon as inline SVG with proper Carbon Design System attributes.

    Automatically adds Carbon-required attributes:
    - fill="currentColor" - Inherit color from CSS
    - focusable="false" - Remove from tab order
    - preserveAspectRatio="xMidYMid meet" - Proper scaling
    - aria-hidden="true" - Hide from screen readers (decorative)
    - width and height - Explicit dimensions

    Args:viewbox
        name: Icon name (e.g., 'edit', 'add', 'close')
        size: Icon size (16, 20, 24, or 32)
        viewbox: The library's default viewbox size (64)
        **attrs: Additional HTML attributes to add to <svg> tag
                 (overrides defaults if provided)

    Returns:
        SVG markup with attributes injected, or empty string if icon not found

    Raises:
        ImproperlyConfigured: If CARBON_ICONS_PATH is not configured properly

    Examples:
        >>> render_carbon_icon_svg('add', 16, slot='icon', class_='my-icon')
        '<svg fill="currentColor" width="16" height="16" slot="icon" class="my-icon" ...>...</svg>'
    """

    # This may raise ImproperlyConfigured - let it bubble up
    svg_markup = read_carbon_icon_svg(name, viewbox)
    if not svg_markup:
        return ""

    if "class_" in attrs:
        attrs["class"] = attrs.pop("class_")

    # Carbon Design System standard attributes
    # These match what @carbon/icons ES modules provide
    carbon_attrs = {
        "fill": "currentColor",
        "focusable": "false",
        "preserveAspectRatio": "xMidYMid meet",
        "aria-hidden": "true",
        "width": str(size),
        "height": str(size),
    }

    # Merge user attrs (user attrs override defaults)
    carbon_attrs.update(attrs)

    # Build attribute string
    attr_parts = [f'{k}="{v}"' for k, v in carbon_attrs.items()]
    attr_string = " " + " ".join(attr_parts)

    svg_markup = svg_markup.replace(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="',
        f'<svg xmlns="http://www.w3.org/2000/svg" {attr_string} viewBox="',
        1,
    )

    return svg_markup
