from django.forms import widgets

from .base import CarbonWidgetMixin


class CarbonTextarea(CarbonWidgetMixin, widgets.Textarea):
    """
    Carbon Design System textarea widget for Django forms.

    Supports all cds-textarea attributes, including validation,
    state management, and visual customisation.
    """

    template_name = "django_zooy/carbon/widgets/textarea.html"

    def __init__(self, attrs=None):
        super().__init__(attrs)
        # Remove Django's default 'cols' and 'rows' attributes
        # Carbon textarea has a drag handle for user-controlled resizing
        if "cols" in self.attrs:
            del self.attrs["cols"]
        if "rows" in self.attrs:
            del self.attrs["rows"]
