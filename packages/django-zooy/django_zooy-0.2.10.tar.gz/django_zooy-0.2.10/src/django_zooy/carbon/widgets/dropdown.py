from django.forms import widgets

from .base import CarbonWidgetMixin


class CarbonDropdown(CarbonWidgetMixin, widgets.Select):
    """
    Carbon Design System dropdown widget for Django forms.

    Uses <cds-dropdown> web component with <cds-dropdown-item> children.

    Documentation:
    https://web-components.carbondesignsystem.com/?path=/docs/components-dropdown

    Example usage:
        class MyForm(CarbonFormMixin, forms.Form):
            network = forms.ChoiceField(
                choices=NETWORK_CHOICES,
                widget=CarbonDropdown()
            )
    """

    template_name = "django_zooy/carbon/widgets/dropdown.html"

    # Dropdown types
    # Sometimes you will need to place a dropdown inline with other content.
    # To do that, add type="inline" to the dropdown.
    TYPE_DEFAULT = "default"
    TYPE_INLINE = "inline"

    # Dropdown sizes
    # This drives the space between the options in the dropdown list
    SIZE_SMALL = "sm"
    SIZE_MEDIUM = "md"
    SIZE_LARGE = "lg"
