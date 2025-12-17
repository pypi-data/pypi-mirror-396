from __future__ import annotations

from typing import TYPE_CHECKING

from .block import Block

if TYPE_CHECKING:
    from .document import Document


class Edge(Block):
    """Graph edge, renders as @edge."""

    _fields = Block._fields | frozenset({"from_id", "to_id", "rel", "render_edge"})

    def __init__(
        self,
        id: str,
        from_id: str,
        to_id: str,
        rel: str,
        type: str = "edge",
        lang: str | None = None,
        meta: dict[str, str] | None = None,
        content: str = "",
        render_edge: bool = True,
        _doc: Document | None = None,
        **kwargs: str,
    ) -> None:
        super().__init__(id, type, lang, meta, content, _doc, **kwargs)
        self.from_id = from_id
        self.to_id = to_id
        self.rel = rel
        self.render_edge = render_edge

    def render_header(self) -> str:
        """Return @edge header line."""
        parts = ["@edge", self.id, self.from_id, "->", self.to_id, self.rel]
        if self.lang:
            parts.append(self.lang)
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"Edge(id={self.id!r}, from_id={self.from_id!r}, to_id={self.to_id!r}, rel={self.rel!r})"
