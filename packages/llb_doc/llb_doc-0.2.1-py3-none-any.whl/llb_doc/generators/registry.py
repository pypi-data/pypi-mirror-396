from __future__ import annotations

import asyncio
import inspect
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..cache.cache import GeneratorCache
    from ..core.block import Block
    from ..core.document import Document

MetaGenerator = Callable[["Block"], str] | Callable[["Block"], "asyncio.Future[str]"]


class GeneratorRegistry:
    def __init__(self, cache: GeneratorCache | None = None) -> None:
        self._generators: dict[str, MetaGenerator] = {}
        self._cache = cache

    def register(self, meta_key: str, func: MetaGenerator) -> None:
        self._generators[meta_key] = func

    def get(self, meta_key: str) -> MetaGenerator | None:
        return self._generators.get(meta_key)

    def set_cache(self, cache: GeneratorCache | None) -> None:
        self._cache = cache

    async def apply(self, block: Block, *, force: bool = False) -> None:
        for key, gen in self._generators.items():
            if not force and key in block.meta:
                continue
            if not force and self._cache:
                cached = self._cache.get(block, key)
                if cached is not None:
                    block.meta[key] = cached
                    continue
            result = gen(block)
            if inspect.isawaitable(result):
                result = await result
            block.meta[key] = result
            if self._cache:
                self._cache.set(block, key, result)

    async def apply_all(self, doc: Document, *, force: bool = False) -> None:
        await asyncio.gather(*[self.apply(b, force=force) for b in doc.blocks])


META_KEY_ATTR = "__llb_meta_key__"


def meta_generator(meta_key: str):
    def decorator(func: MetaGenerator) -> MetaGenerator:
        setattr(func, META_KEY_ATTR, meta_key)
        return func

    return decorator


def get_meta_key(func: MetaGenerator) -> str | None:
    return getattr(func, META_KEY_ATTR, None)
