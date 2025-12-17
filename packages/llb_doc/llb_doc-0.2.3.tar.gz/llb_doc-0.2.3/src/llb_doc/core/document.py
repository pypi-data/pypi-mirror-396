from __future__ import annotations

import asyncio
from enum import Enum
from typing import Self

from .block import Block

from ..generators.registry import GeneratorRegistry, MetaGenerator, get_meta_key
from ..sorters.registry import BlockSorter, SorterRegistry, get_sorter_name


class MetaRefreshMode(Enum):
    NONE = "none"
    NORMAL = "normal"
    FORCE = "force"


DEFAULT_DOC_PREFIX = """# Document
Each block follows this structure:
```
@block <id> <type> [lang]
key1=value1
key2=value2

<content>

@end <id>
```"""


class DuplicateIDError(ValueError):
    """Raised when attempting to add a block with a duplicate ID."""

    def __init__(self, id_: str) -> None:
        super().__init__(f"Block with ID '{id_}' already exists")
        self.id = id_


class BlockNotFoundError(KeyError):
    """Raised when a block with the given ID is not found."""

    def __init__(self, id_: str) -> None:
        super().__init__(f"Block with ID '{id_}' not found")
        self.id = id_


class IDGenerator:
    def __init__(self, prefix: str = "B") -> None:
        self._prefix = prefix
        self._counter = 0

    def next(self) -> str:
        self._counter += 1
        return f"{self._prefix}{self._counter:X}"


class BlockBuilder:
    def __init__(self, doc: Document, type_: str, lang: str | None = None) -> None:
        self._doc = doc
        self._id: str | None = None
        self._type = type_
        self._lang = lang
        self._meta: dict[str, str] = {}
        self._content: str = ""

    def id(self, id_: str) -> Self:
        self._id = id_
        return self

    def meta(self, **kwargs: str) -> Self:
        self._meta.update(kwargs)
        return self

    def content(self, text: str) -> Self:
        self._content = text
        return self

    def add(self) -> Block:
        block_id = self._id or self._doc._generate_unique_id()
        self._doc._validate_unique_id(block_id)
        block = Block(
            id=block_id,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            _doc=self._doc,
        )
        self._doc._block_order.append(block_id)
        self._doc._id_index[block_id] = block
        return block

    def __enter__(self) -> Block:
        block_id = self._id or self._doc._generate_unique_id()
        self._doc._validate_unique_id(block_id)
        self._block = Block(
            id=block_id,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            _doc=self._doc,
        )
        return self._block

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self._doc._block_order.append(self._block.id)
            self._doc._id_index[self._block.id] = self._block


class Document:
    def __init__(
        self,
        generators: list[MetaGenerator] | None = None,
        sorters: list[BlockSorter] | None = None,
    ) -> None:
        self._block_order: list[str] = []
        self._id_index: dict[str, Block] = {}
        self._id_gen = IDGenerator()
        self._generator_registry: GeneratorRegistry = GeneratorRegistry()
        self._sorter_registry: SorterRegistry = SorterRegistry()
        self._prefix: str = ""
        self._suffix: str = ""
        if generators:
            for gen in generators:
                meta_key = get_meta_key(gen)
                if meta_key is None:
                    raise ValueError(
                        f"Function {gen.__name__} is not decorated with @meta_generator"
                    )
                self._generator_registry.register(meta_key, gen)
        if sorters:
            for sorter in sorters:
                sorter_name = get_sorter_name(sorter)
                if sorter_name is None:
                    raise ValueError(
                        f"Function {sorter.__name__} is not decorated with @block_sorter"
                    )
                self._sorter_registry.register(sorter_name, sorter)

    @property
    def prefix(self) -> str:
        return self._prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        self._prefix = value

    @property
    def suffix(self) -> str:
        return self._suffix

    @suffix.setter
    def suffix(self, value: str) -> None:
        self._suffix = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Document):
            return NotImplemented
        return (
            self._prefix == other._prefix
            and self._suffix == other._suffix
            and self.blocks == other.blocks
        )

    def __len__(self) -> int:
        return len(self._block_order)

    def __contains__(self, id_: str) -> bool:
        return id_ in self._id_index

    def __getitem__(self, id_: str) -> Block:
        if id_ not in self._id_index:
            raise BlockNotFoundError(id_)
        return self._id_index[id_]

    def __iter__(self):
        return (self._id_index[id_] for id_ in self._block_order)

    @property
    def blocks(self) -> list[Block]:
        return [self._id_index[id_] for id_ in self._block_order]

    def _validate_unique_id(self, id_: str) -> None:
        if id_ in self._id_index:
            raise DuplicateIDError(id_)

    def _generate_unique_id(self) -> str:
        while True:
            id_ = self._id_gen.next()
            if id_ not in self._id_index:
                return id_

    def block(self, type_: str, lang: str | None = None) -> BlockBuilder:
        return BlockBuilder(self, type_, lang)

    def add_block(
        self,
        type_: str,
        content: str = "",
        *,
        lang: str | None = None,
        id_: str | None = None,
        **meta: str,
    ) -> Block:
        block_id = id_ or self._generate_unique_id()
        self._validate_unique_id(block_id)
        block = Block(
            id=block_id,
            type=type_,
            lang=lang,
            meta=meta,
            content=content,
            _doc=self,
        )
        self._block_order.append(block_id)
        self._id_index[block_id] = block
        return block

    def get_block(self, id_: str) -> Block | None:
        """Get a block by ID, returns None if not found."""
        return self._id_index.get(id_)

    def has_block(self, id_: str) -> bool:
        """Check if a block with the given ID exists."""
        return id_ in self._id_index

    def remove_block(self, id_: str) -> Block:
        """Remove and return a block by ID. Raises BlockNotFoundError if not found."""
        if id_ not in self._id_index:
            raise BlockNotFoundError(id_)
        block = self._id_index.pop(id_)
        self._block_order.remove(id_)
        block._doc = None
        return block

    def replace_block(
        self,
        id_: str,
        type_: str | None = None,
        content: str | None = None,
        *,
        lang: str | None = ...,  # type: ignore[assignment]
        **meta: str,
    ) -> Block:
        """Replace/update a block in place. Raises BlockNotFoundError if not found."""
        if id_ not in self._id_index:
            raise BlockNotFoundError(id_)
        block = self._id_index[id_]
        if type_ is not None:
            block.type = type_
        if content is not None:
            block.content = content
        if lang is not ...:
            block.lang = lang
        if meta:
            block.meta.update(meta)
        return block

    def set_block(
        self,
        id_: str,
        type_: str,
        content: str = "",
        *,
        lang: str | None = None,
        **meta: str,
    ) -> Block:
        """Set a block by ID. Creates if not exists, replaces entirely if exists."""
        if id_ in self._id_index:
            old_block = self._id_index[id_]
            new_block = Block(
                id=id_,
                type=type_,
                lang=lang,
                meta=meta,
                content=content,
                _doc=self,
            )
            self._id_index[id_] = new_block
            old_block._doc = None
            return new_block
        else:
            return self.add_block(type_, content, lang=lang, id_=id_, **meta)

    def move_block(self, id_: str, position: int) -> None:
        """Move a block to a specific position (0-indexed)."""
        if id_ not in self._id_index:
            raise BlockNotFoundError(id_)
        self._block_order.remove(id_)
        self._block_order.insert(position, id_)

    def swap_blocks(self, id1: str, id2: str) -> None:
        """Swap positions of two blocks."""
        if id1 not in self._id_index:
            raise BlockNotFoundError(id1)
        if id2 not in self._id_index:
            raise BlockNotFoundError(id2)
        idx1 = self._block_order.index(id1)
        idx2 = self._block_order.index(id2)
        self._block_order[idx1], self._block_order[idx2] = id2, id1

    def reorder_blocks(self, ids: list[str]) -> None:
        """Reorder blocks according to the given ID list. All IDs must be present."""
        if set(ids) != set(self._id_index.keys()):
            missing = set(self._id_index.keys()) - set(ids)
            extra = set(ids) - set(self._id_index.keys())
            if missing:
                raise ValueError(f"Missing block IDs in reorder list: {missing}")
            if extra:
                raise BlockNotFoundError(list(extra)[0])
        self._block_order = list(ids)

    def _render_body(self, *, order: str | None = None) -> str:
        """Build rendered document body."""
        blocks = self.blocks
        if order is not None:
            blocks = self._sorter_registry.apply(blocks, order)

        rendered_blocks = [b.render() for b in blocks]
        body = "\n\n".join(rendered_blocks)

        parts: list[str] = []
        if self._prefix:
            parts.append(self._prefix)
            parts.append("---")
        if body:
            parts.append(body)
        if self._suffix:
            parts.append("---")
            parts.append(self._suffix)
        return "\n\n".join(parts)

    def render(
        self,
        *,
        order: str | None = None,
        meta_refresh: MetaRefreshMode = MetaRefreshMode.NORMAL,
    ) -> str:
        """Render document to LLB format string (sync version)."""
        if meta_refresh != MetaRefreshMode.NONE:
            force = meta_refresh == MetaRefreshMode.FORCE
            asyncio.run(self.ensure_meta(force=force))
        return self._render_body(order=order)

    async def arender(
        self,
        *,
        order: str | None = None,
        meta_refresh: MetaRefreshMode = MetaRefreshMode.NORMAL,
    ) -> str:
        """Async version of render()."""
        if meta_refresh != MetaRefreshMode.NONE:
            force = meta_refresh == MetaRefreshMode.FORCE
            await self.ensure_meta(force=force)
        return self._render_body(order=order)

    async def ensure_meta(self, *, force: bool = False) -> None:
        """Apply generators to all blocks."""
        await self._generator_registry.apply_all(self, force=force)


def create_llb(
    *,
    generators: list[MetaGenerator] | None = None,
    sorters: list[BlockSorter] | None = None,
) -> Document:
    return Document(generators, sorters)
