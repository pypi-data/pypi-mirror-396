from typing import ClassVar, Union, Literal
from pydantic import Field
from dominate.tags import button

from pysty.base import Component

# IDE-only presets (not runtime enums)
ButtonSize = Literal["xs", "sm", "md", "lg", "xl"]
ButtonVariant = Literal[
    "default",
    "secondary",
    "tertiary",
    "success",
    "danger",
    "warning",
    "dark",
    "ghost",
]

# Small, explicit resolver
def resolve(value: str, mapping: dict[str, str]) -> str:
    """
    Resolve semantic key to Tailwind classes.
    Falls back to raw value if key is unknown.
    """
    return mapping.get(value, value)

class DefaultButton(Component):
    """
    Pysty DefaultButton

    - String-first API
    - Semantic presets with IDE autocomplete
    - Full Tailwind override support
    - Explicit, predictable behavior
    """

    # Internal preset maps
    _SIZE_MAP = {
        "xs": "text-xs px-2 py-1",
        "sm": "text-xs px-3 py-1.5",
        "md": "text-sm px-4 py-2.5",
        "lg": "text-base px-5 py-3",
        "xl": "text-lg px-6 py-4",
    }

    _VARIANT_MAP = {
        "default": (
            "text-white bg-blue-600 border border-transparent "
            "hover:bg-blue-700 focus:ring-4 focus:ring-blue-300"
        ),
        "secondary": (
            "text-gray-700 bg-gray-200 border border-gray-300 "
            "hover:bg-gray-300 hover:text-gray-900 focus:ring-4 focus:ring-gray-100"
        ),
        "tertiary": (
            "text-gray-600 bg-gray-100 border border-gray-200 "
            "hover:bg-gray-200 hover:text-gray-900 focus:ring-4 focus:ring-gray-100"
        ),
        "success": (
            "text-white bg-green-600 border border-transparent "
            "hover:bg-green-700 focus:ring-4 focus:ring-green-300"
        ),
        "danger": (
            "text-white bg-red-600 border border-transparent "
            "hover:bg-red-700 focus:ring-4 focus:ring-red-300"
        ),
        "warning": (
            "text-white bg-yellow-500 border border-transparent "
            "hover:bg-yellow-600 focus:ring-4 focus:ring-yellow-300"
        ),
        "dark": (
            "text-white bg-gray-800 border border-transparent "
            "hover:bg-gray-900 focus:ring-4 focus:ring-gray-500"
        ),
        "ghost": (
            "text-gray-700 bg-transparent border border-transparent "
            "hover:bg-gray-100 focus:ring-4 focus:ring-gray-200"
        ),
    }

    # Base classes
    BASE_CLASSES: ClassVar[str] = (
        "box-border font-medium leading-5 rounded-lg shadow-sm "
        "focus:outline-none transition-colors"
    )

    # Public API (user facing)
    label: str = Field(...)
    size: Union[ButtonSize, str] = Field(
        default="md",
        description=(
            "Preset size (xs|sm|md|lg|xl) or custom Tailwind classes."
        ),
    )
    variant: Union[ButtonVariant, str] = Field(
        default="default",
        description=(
            "Preset variant or custom Tailwind classes."
        ),
    )
    type: Literal["button", "submit", "reset"] = Field(
        default="button",
        description="HTML button type.",
    )

    # Rendering
    def html_attributes(self) -> dict:
        size_cls = resolve(self.size, self._SIZE_MAP)
        variant_cls = resolve(self.variant, self._VARIANT_MAP)
        return {
            "class": f"{self.BASE_CLASSES} {size_cls} {variant_cls}",
            "type": self.type,
        }

    def render(self) -> str:
        return button(
            self.label,
            **self._combined_attributes()
        ).render()
