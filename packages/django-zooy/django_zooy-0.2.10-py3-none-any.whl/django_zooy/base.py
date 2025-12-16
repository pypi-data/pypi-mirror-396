"""
Base classes and mixins for django-zooy integration.

This module provides core functionality that's shared across
different widget library integrations (Carbon, MDC, etc.).
"""


class ZooyFormMixin:
    """
    Base mixin for Django forms that integrate with Zooy UI framework.

    This mixin provides common functionality for forms that use
    Zooy-integrated widgets across different design systems.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_zooy_widgets()

    def _configure_zooy_widgets(self):
        """
        Configure Zooy-specific widget settings.

        This method can be overridden by subclasses to add
        additional widget configuration logic.
        """
        pass


__all__ = [
    "ZooyFormMixin",
]
