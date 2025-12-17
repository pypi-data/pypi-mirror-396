from __future__ import annotations

from typing import TYPE_CHECKING

from .block import Block

if TYPE_CHECKING:
    from .document import Document


class Ctx(Block):
    """Graph context block, renders as @ctx."""

    _fields = Block._fields | frozenset({"focus", "radius", "strategy", "tiers"})

    def __init__(
        self,
        id: str,
        type: str = "ctx",
        lang: str | None = None,
        meta: dict[str, str] | None = None,
        content: str = "",
        focus: str | None = None,
        radius: int | None = None,
        strategy: str | None = None,
        tiers: str | None = None,
        _doc: Document | None = None,
        **kwargs: str,
    ) -> None:
        super().__init__(id, type, lang, meta, content, _doc, **kwargs)
        self.focus = focus
        self.radius = radius
        self.strategy = strategy
        self.tiers = tiers

    def render_header(self) -> str:
        """Return @ctx header line."""
        return f"@ctx {self.id}"

    def render_meta(self) -> list[str]:
        """Return focus, radius, strategy and tiers meta lines."""
        lines: list[str] = []
        if self.focus is not None:
            lines.append(f"focus={self.focus}")
        if self.radius is not None:
            lines.append(f"radius={self.radius}")
        if self.strategy is not None:
            lines.append(f"strategy={self.strategy}")
        if self.tiers is not None:
            if "\n" in self.tiers:
                lines.append(f'tiers="""\n{self.tiers}\n"""')
            else:
                lines.append(f"tiers={self.tiers}")
        return lines

    def __repr__(self) -> str:
        return f"Ctx(id={self.id!r}, focus={self.focus!r}, radius={self.radius!r})"
