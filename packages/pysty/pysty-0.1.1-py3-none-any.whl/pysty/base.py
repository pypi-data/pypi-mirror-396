from abc import ABC, abstractmethod
from typing import Any, ClassVar
from pydantic import BaseModel, Field

def _to_html_attr(name: str) -> str:
    """Convert Python attr name to HTML: hx_swap_oob → hx-swap-oob, class_ → class"""
    return name.rstrip("_").replace("_", "-")

class Component(BaseModel, ABC):
    """
    Base class for all Pysty UI components.
    """

    # HTMX core – request methods
    hx_get: str | None = Field(default=None)
    hx_post: str | None = Field(default=None)
    hx_put: str | None = Field(default=None)
    hx_patch: str | None = Field(default=None)
    hx_delete: str | None = Field(default=None)

    # HTMX core – trigger & target
    hx_trigger: str | None = Field(default=None)
    hx_target: str | None = Field(default=None)
    hx_swap: str | None = Field(default=None)

    # HTMX core – content selection
    hx_select: str | None = Field(default=None)
    hx_select_oob: str | None = Field(default=None)
    hx_swap_oob: str | None = Field(default=None)

    # HTMX core – data & values
    hx_vals: str | None = Field(default=None)
    hx_headers: str | None = Field(default=None)
    hx_include: str | None = Field(default=None)
    hx_params: str | None = Field(default=None)
    hx_encoding: str | None = Field(default=None)

    # HTMX core – URL & history
    hx_push_url: str | None = Field(default=None)
    hx_replace_url: str | None = Field(default=None)
    hx_history: str | None = Field(default=None)
    hx_history_elt: str | None = Field(default=None)

    # HTMX UX – user feedback
    hx_confirm: str | None = Field(default=None)
    hx_prompt: str | None = Field(default=None)
    hx_indicator: str | None = Field(default=None)
    hx_disabled_elt: str | None = Field(default=None)

    # HTMX UX – progressive enhancement
    hx_boost: str | None = Field(default=None)
    hx_preserve: str | None = Field(default=None)

    # HTMX request control
    hx_sync: str | None = Field(default=None)
    hx_validate: str | None = Field(default=None)
    hx_request: str | None = Field(default=None)
    hx_ext: str | None = Field(default=None)

    # HTMX inheritance control
    hx_disinherit: str | None = Field(default=None)
    hx_inherit: str | None = Field(default=None)
    hx_disable: str | None = Field(default=None)

    # HTMX event handling
    hx_on: str | None = Field(default=None)

    # Internal – cache HTMX field names for performance
    _htmx_field_names: ClassVar[tuple[str, ...]] = ()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Cache HTMX field names when subclass is created (runs once per class)."""
        super().__init_subclass__(**kwargs)
        cls._htmx_field_names = tuple(
            name for name in cls.model_fields if name.startswith("hx_")
        )

    def _htmx_attributes(self) -> dict[str, str]:
        """Collect non-None HTMX attributes as HTML-ready dict."""
        return {
            _to_html_attr(name): str(value)
            for name in self._htmx_field_names
            if (value := getattr(self, name, None)) is not None
        }

    def html_attributes(self) -> dict[str, Any]:
        """Override to add custom HTML attributes (class, id, data-*, aria-*, etc.)."""
        return {}

    def _combined_attributes(self) -> dict[str, Any]:
        """Merge HTMX + custom HTML attributes for Dominate rendering."""
        return {**self._htmx_attributes(), **self.html_attributes()}

    @abstractmethod
    def render(self) -> str:
        """Return HTML string. Typically: return div(...).render()"""
        ...
