from ..base import ZooyFormMixin


class CarbonFormMixin(ZooyFormMixin):
    """
    Mixin for Django forms that use Carbon Design System widgets.

    Automatically injects Carbon Design System attributes from Django form fields,
    eliminating boilerplate configuration in form __init__ methods.
    """

    def _configure_zooy_widgets(self):
        """
        Inject Carbon Design System attributes into widget attributes.

        Automatically configures:
        - label: Field label text
        - required: Required field indicator
        - helper-text: Help text for the field
        - disabled: Disabled state
        - readonly: Read-only state
        - placeholder: Placeholder text (if not already set)
        """
        super()._configure_zooy_widgets()

        for _field_name, field in self.fields.items():
            widget = field.widget

            # Only inject for Carbon widgets
            if self._is_carbon_widget(widget):
                # Inject label
                widget.attrs.update(label=field.label)

                # Inject the required attribute
                if field.required:
                    widget.attrs.update(required=True)

                # Inject helper text (from field.help_text)
                if field.help_text:
                    widget.attrs.update({"helper-text": field.help_text})

                # Inject max_length as max-count (for character counting)
                # Note: max-count only has an effect when enable-counter is True
                # Use setdefault to allow manual override
                if hasattr(field, "max_length") and field.max_length:
                    widget.attrs.setdefault("max-count", field.max_length)

                # Inject disabled state
                if field.disabled:
                    widget.attrs.update(disabled=True)

    def _inject_errors_into_widgets(self):
        """
        Inject validation errors into Carbon widget attributes.

        This should be called after validation (after is_valid() is called).
        """
        for field_name, field in self.fields.items():
            widget = field.widget

            if self._is_carbon_widget(widget):
                # Check if this field has errors
                if field_name in self.errors:
                    error_list = self.errors[field_name]
                    widget.attrs.update(
                        {
                            "invalid": "",  # Boolean attribute
                            "invalid-text": " ".join(error_list),
                        }
                    )

    def is_valid(self):
        """
        Override is_valid to inject errors after validation.
        """
        valid = super().is_valid()

        # After validation, inject errors into widget attributes
        if not valid:
            self._inject_errors_into_widgets()

        return valid

    @staticmethod
    def _is_carbon_widget(widget):
        if not hasattr(widget, "template_name") or not widget.template_name:
            return False

        template_name = widget.template_name.lower()
        return "carbon" in template_name or "django_zooy" in template_name


__all__ = [
    "CarbonFormMixin",
]
