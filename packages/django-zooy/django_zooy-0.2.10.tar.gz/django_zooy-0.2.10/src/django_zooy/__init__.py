"""
django-zooy: Django integration for Zooy UI framework

Provides Django form widgets and mixins for seamlessly integrating
Carbon Design System and other UI frameworks with Django forms and the
Zooy JavaScript UI framework.
"""

from .base import ZooyFormMixin
from .carbon import CarbonFormMixin

__version__ = "0.1.0"
__all__ = [
    "ZooyFormMixin",
    "CarbonFormMixin",
]
