from __future__ import annotations

from typing import TYPE_CHECKING

from .block import Block

if TYPE_CHECKING:
    from .document import Document


class Node(Block):
    """Graph node, renders as @node."""

    _fields = Block._fields | frozenset({"tier", "in_edges", "out_edges"})

    def __init__(
        self,
        id: str,
        type: str,
        lang: str | None = None,
        meta: dict[str, str] | None = None,
        content: str = "",
        _doc: Document | None = None,
        **kwargs: str,
    ) -> None:
        super().__init__(id, type, lang, meta, content, _doc, **kwargs)
        self.tier: int | None = None
        self.in_edges: list[str] = []
        self.out_edges: list[str] = []

    def render_header(self) -> str:
        """Return @node header line."""
        parts = ["@node", self.id, self.type]
        if self.lang:
            parts.append(self.lang)
        return " ".join(parts)

    def render_meta(self) -> list[str]:
        """Return tier and edges meta lines."""
        return [
            f"tier={self.tier}",
            f"in_edges={self.in_edges!r}",
            f"out_edges={self.out_edges!r}",
        ]

    def __repr__(self) -> str:
        return f"Node(id={self.id!r}, type={self.type!r}, lang={self.lang!r}, meta={self.meta!r}, content={self.content!r})"
