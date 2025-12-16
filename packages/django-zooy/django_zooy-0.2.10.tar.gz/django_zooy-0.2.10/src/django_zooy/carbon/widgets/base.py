"""
Base classes for Carbon Design System widgets.
"""

from django.utils.html import escape
from django.utils.text import slugify


class CarbonWidgetMixin:
    """
    Mixin providing common functionality for Carbon Design System widgets.

    Handles:
    - Attribute name conversion (snake_case to kebab-case)
    - Boolean attribute rendering
    - Attribute string building
    """

    # Supported Carbon widget sizes
    SIZE_SMALL = "sm"
    SIZE_MEDIUM = "md"
    SIZE_LARGE = "lg"

    def get_context(self, name, value, attrs):
        """
        Build the context for rendering Carbon widgets.

        Processes all Django and Carbon-specific attributes and creates
        an attribute string ready for HTML rendering.
        """
        context = super().get_context(name, value, attrs)

        # Preserve input type if it exists (for text inputs)
        if hasattr(self, "input_type"):
            context["widget"]["input_type"] = self.input_type

        # Build all attributes into a single string
        widget_attrs = context["widget"]["attrs"]
        attr_string = self._build_attr_string(widget_attrs, name, value)

        context["widget"]["attr_string"] = attr_string

        return context

    def _build_attr_string(self, attrs, name, value):
        """
        Build HTML attribute string from attrs dict.

        Handles:
        - Boolean attributes (rendered without values)
        - Standard key-value attributes
        - Special Carbon attributes
        - Automatic kebab-case conversion
        """
        parts = []

        # Always include name attribute
        parts.append(f'name="{escape(name)}"')

        # Include value if present
        if value is not None and value != "":
            parts.append(f'value="{escape(value)}"')

        # Process all other attributes
        for key, val in attrs.items():
            # Skip 'name' and 'value' as we've already handled them
            if key in ("name", "value"):
                continue

            # Convert Python naming to Carbon's kebab-case
            carbon_key = self._to_carbon_attribute(key)

            # Handle boolean attributes
            if val is True or val == "":
                parts.append(carbon_key)
            elif val is False or val is None:
                # Skip false/none boolean attributes
                continue
            else:
                # Regular key-value attribute
                parts.append(f'{carbon_key}="{escape(str(val))}"')

        return " ".join(parts)

    def _to_carbon_attribute(self, attr_name):
        """
        Convert Python attribute names to Carbon's kebab-case format.

        Examples:
        - helper_text -> helper-text
        - invalid_text -> invalid-text
        - show_password_visibility_toggle -> show-password-visibility-toggle
        """
        # Handle special cases that shouldn't be slugified
        special_cases = {
            "type": "type",
            "placeholder": "placeholder",
            "id": "id",
            "class": "class",
            "rows": "rows",
            "cols": "cols",
        }

        if attr_name in special_cases:
            return special_cases[attr_name]

        # Convert underscores to hyphens and slugify
        return slugify(attr_name).replace("_", "-").lower()

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Override to provide sensible defaults for Carbon attributes.
        """
        attrs = super().build_attrs(base_attrs, extra_attrs)

        # Set default size if not specified
        if "size" not in attrs:
            attrs["size"] = self.SIZE_MEDIUM

        return attrs
