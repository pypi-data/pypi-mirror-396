from django.forms import widgets

from .base import CarbonWidgetMixin


class CarbonTextInput(CarbonWidgetMixin, widgets.TextInput):
    """
    Carbon Design System text input widget for Django forms.

    Supports all cds-text-input attributes, including validation,
    state management, and visual customisation.
    """

    template_name = "django_zooy/carbon/widgets/text_input.html"

    # Supported tooltip alignments
    TOOLTIP_ALIGN_START = "start"
    TOOLTIP_ALIGN_CENTER = "center"
    TOOLTIP_ALIGN_END = "end"

    # Supported tooltip directions
    TOOLTIP_DIR_TOP = "top"
    TOOLTIP_DIR_RIGHT = "right"
    TOOLTIP_DIR_BOTTOM = "bottom"
    TOOLTIP_DIR_LEFT = "left"


class CarbonEmailInput(CarbonTextInput):
    """Carbon email input widget."""

    input_type = "email"


class CarbonPasswordInput(CarbonTextInput):
    """
    Carbon password input widget.

    Automatically enables the password visibility toggle by default.
    """

    input_type = "password"
    template_name = "django_zooy/carbon/widgets/password_input.html"

    def __init__(self, attrs=None, render_value=False):
        if attrs is None:
            attrs = {}

        # Enable password visibility toggle by default
        if "show_password_visibility_toggle" not in attrs:
            attrs["show_password_visibility_toggle"] = True

        super().__init__(attrs)
        self.render_value = render_value

    def get_context(self, name, value, attrs):
        if not self.render_value:
            value = None
        return super().get_context(name, value, attrs)


class CarbonURLInput(CarbonTextInput):
    """Carbon URL input widget."""

    input_type = "url"


class CarbonTelInput(CarbonTextInput):
    """Carbon telephone input widget."""

    input_type = "tel"


class CarbonNumberInput(CarbonTextInput):
    """Carbon number input widget."""

    input_type = "number"


class CarbonSearchInput(CarbonTextInput):
    """Carbon search input widget."""

    input_type = "search"
