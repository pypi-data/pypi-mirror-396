# ============================================================================
# Carbon Design System Icons
# ============================================================================
from django import template
from django.utils.safestring import mark_safe

from ..carbon.icons import render_carbon_icon_svg

register = template.Library()


@register.simple_tag
def carbon_icon(name, size=16, viewbox=32, toggle_to=None, **kwargs):
    """
    Render a Carbon Design System icon as inline SVG.

    This reads the SVG file from @carbon/icons and renders it directly
    in your template. No JavaScript, no CDN, no placeholders.

    Usage in template:
        {% load carbon %}
        {% carbon_icon "edit" size=16 slot="icon" %}
        {% carbon_icon "add" 20 class="my-icon" %}
        {% carbon_icon "save" %}  {# defaults to size 16 #}

        {# For toggleable icons (e.g., favorite/unfavorite) #}
        {% carbon_icon "favorite" 16 slot="icon" toggle_to="favorite--filled" %}

    Args:
        name: Icon name (e.g., 'edit', 'add', 'close')
        size: Icon size (16, 20, 24, or 32)
        viewbox: The library's default viewbox size.
                Determines the directory the icon will be searched in (32)
        toggle_to: Optional icon name to toggle to (e.g., 'favorite--filled').
                  When provided, renders both icons wrapped in a span with
                  CSS classes for zooy to toggle visibility.
        **kwargs: Additional HTML attributes (slot, class, data-*, etc.)

    Browse icons: https://carbondesignsystem.com/guidelines/icons/library/
    """
    if not toggle_to:
        # Simple icon - render and return
        # Safe: SVG content is from trusted Carbon Design System files
        return mark_safe(render_carbon_icon_svg(name, size, viewbox, **kwargs))  # nosec B308 B703

    # Toggle mode - render two icons wrapped in a span
    slot_attr = kwargs.pop("slot", None)
    current_class = kwargs.get("class", "")

    # Render off-state icon
    kwargs["class"] = f"{current_class} off-icon".strip()
    off_svg = render_carbon_icon_svg(name, size, viewbox, **kwargs)

    # Render on-state icon
    kwargs["class"] = "on-icon"
    on_svg = render_carbon_icon_svg(toggle_to, size, viewbox, **kwargs)

    # Wrap both in span with slot attribute
    # Safe: SVG content is from trusted Carbon Design System files
    slot_html = f' slot="{slot_attr}"' if slot_attr else ""
    return mark_safe(f'<span{slot_html} class="icon-toggle-wrapper">{off_svg}{on_svg}</span>')  # nosec B308 B703
