# pysty/text.py
from pydantic import Field
from dominate.tags import p
from pysty.base import Component


class Text(Component):
    """
    Simple text component.
    """

    value: str = Field(
        ...,
        description="Text content. Example: 'Hello world'",
    )

    classes: str = Field(
        default="text-gray-600",
        description="Tailwind classes. Example: 'text-sm text-gray-500'",
    )

    def html_attributes(self) -> dict:
        return {"class": self.classes}

    def render(self) -> str:
        return p(self.value, **self._combined_attributes()).render()
