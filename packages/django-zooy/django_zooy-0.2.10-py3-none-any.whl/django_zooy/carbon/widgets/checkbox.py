from django.forms import widgets
from django.utils.html import escape

from .base import CarbonWidgetMixin


class CarbonCheckboxSelectMultiple(CarbonWidgetMixin, widgets.CheckboxSelectMultiple):
    """
    Carbon Design System checkbox group widget for Django forms.

    Renders multiple <cds-checkbox> elements within a <cds-checkbox-group>.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-checkbox

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            services = forms.MultipleChoiceField(
                choices=SERVICE_CHOICES,
                widget=CarbonCheckboxSelectMultiple()
            )
    """

    template_name = "django_zooy/carbon/widgets/checkbox_select_multiple.html"
    option_template_name = "django_zooy/carbon/widgets/checkbox_option.html"

    def get_context(self, name, value, attrs):
        """Build context including group-level attributes for cds-checkbox-group."""
        context = super().get_context(name, value, attrs)

        # Build group attributes for <cds-checkbox-group>
        # Note: For CheckboxSelectMultiple, CarbonFormMixin injects into self.attrs
        # rather than the attrs parameter passed to get_context
        group_attrs_parts = []

        # Get label for legend-text (injected by CarbonFormMixin into self.attrs)
        if self.attrs.get("label"):
            group_attrs_parts.append(f'legend-text="{escape(self.attrs.get("label"))}"')

        # Get help text (injected by CarbonFormMixin as 'helper-text' into self.attrs)
        if self.attrs.get("helper-text"):
            group_attrs_parts.append(f'helper-text="{escape(self.attrs.get("helper-text"))}"')

        # Handle required state
        if self.attrs.get("required"):
            group_attrs_parts.append("required")

        # Handle validation states (injected by CarbonFormMixin after validation)
        if self.attrs.get("invalid") is not None:
            group_attrs_parts.append("invalid")
            if self.attrs.get("invalid-text"):
                group_attrs_parts.append(f'invalid-text="{escape(self.attrs.get("invalid-text"))}"')

        # Handle warning states
        if self.attrs.get("warn"):
            group_attrs_parts.append("warn")
            if self.attrs.get("warn-text"):
                group_attrs_parts.append(f'warn-text="{escape(self.attrs.get("warn-text"))}"')

        # Handle readonly
        if self.attrs.get("readonly"):
            group_attrs_parts.append("readonly")

        # Handle disabled (injected by CarbonFormMixin)
        if self.attrs.get("disabled"):
            group_attrs_parts.append("disabled")

        # Orientation (vertical is default, so only add if horizontal)
        orientation = self.attrs.get("orientation")
        if orientation == "horizontal":
            group_attrs_parts.append('orientation="horizontal"')

        context["widget"]["group_attrs"] = " ".join(group_attrs_parts)

        return context
