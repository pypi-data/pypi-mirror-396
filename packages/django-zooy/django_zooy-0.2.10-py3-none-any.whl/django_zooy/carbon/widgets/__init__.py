"""
Carbon Design System widgets for Django forms.

These widgets integrate Carbon Design Web Components with Django forms,
providing a seamless integration with the Zooy UI framework.

Documentation:
https://web-components.carbondesignsystem.com/
"""

from .base import CarbonWidgetMixin
from .checkbox import CarbonCheckboxSelectMultiple
from .dropdown import CarbonDropdown
from .text_input import (
    CarbonEmailInput,
    CarbonNumberInput,
    CarbonPasswordInput,
    CarbonSearchInput,
    CarbonTelInput,
    CarbonTextInput,
    CarbonURLInput,
)
from .textarea_input import CarbonTextarea

__all__ = [
    "CarbonWidgetMixin",
    "CarbonTextInput",
    "CarbonEmailInput",
    "CarbonPasswordInput",
    "CarbonURLInput",
    "CarbonTelInput",
    "CarbonNumberInput",
    "CarbonSearchInput",
    "CarbonTextarea",
    "CarbonDropdown",
    "CarbonCheckboxSelectMultiple",
]
