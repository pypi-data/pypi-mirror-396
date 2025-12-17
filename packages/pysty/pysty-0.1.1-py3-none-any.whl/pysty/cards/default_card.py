from typing import Union, List
from pydantic import Field
from dominate.tags import div, h5, p
from dominate.util import raw 

from pysty.base import Component

class DefaultCard(Component):
    """
    Pysty DefaultCard

    - Field-per-style (explicit, override-friendly)
    - String-first Tailwind API
    - No HTML typing
    - Accepts Pysty components as content
    - Works identically with or without HTMX
    """

    # Content
    title: str = Field(...)
    content: Union[str, Component, List[Component]] = Field(...)

    # Layout & container styles
    display: str = Field(default="block")
    width: str = Field(default="max-w-sm")
    padding: str = Field(default="p-6")
    background: str = Field(default="bg-white")
    border: str = Field(default="border border-gray-200")
    radius: str = Field(default="rounded-xl")
    shadow: str = Field(default="shadow-sm")
    hover_shadow: str = Field(default="hover:shadow-md")
    hover_background: str = Field(default="hover:bg-gray-50")
    transitions: str = Field(default="transition-all duration-150")

    # Text styles
    title_classes: str = Field(
        default="mb-3 text-2xl font-semibold tracking-tight text-gray-900 leading-8"
    )
    content_classes: str = Field(
        default="text-gray-600 leading-relaxed"
    )

    # Internal
    _style_fields = [
        "display",
        "width",
        "padding",
        "background",
        "border",
        "radius",
        "shadow",
        "hover_shadow",
        "hover_background",
        "transitions",
    ]

    # Rendering
    def render(self) -> str:
        attrs = self._combined_attributes()
        data = self.model_dump()
        attrs["class"] = " ".join(data[field] for field in self._style_fields)

        with div(**attrs) as card:
            h5(self.title, cls=self.title_classes)

            # Safe composition
            if isinstance(self.content, str):
                p(self.content, cls=self.content_classes)
            elif isinstance(self.content, Component):
                card.add(raw(self.content.render()))
            elif isinstance(self.content, (list, tuple)):
                for item in self.content:
                    if not isinstance(item, Component):
                        raise TypeError(
                            "All items in content list must be Pysty Components"
                        )
                    card.add(raw(item.render()))
            else:
                raise TypeError(
                    "content must be str, Component, or list[Component]"
                )

        return card.render()
