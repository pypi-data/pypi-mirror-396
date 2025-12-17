from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.block import Block


class GeneratorCache:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def _compute_key(self, block: Block, meta_key: str) -> str:
        content_hash = hashlib.sha256(
            f"{block.type}:{block.lang or ''}:{block.content}".encode()
        ).hexdigest()[:16]
        return f"{meta_key}:{content_hash}"

    def get(self, block: Block, meta_key: str) -> str | None:
        key = self._compute_key(block, meta_key)
        return self._cache.get(key)

    def set(self, block: Block, meta_key: str, value: str) -> None:
        key = self._compute_key(block, meta_key)
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)

    def __bool__(self) -> bool:
        return True


_default_cache = GeneratorCache()


def get_default_cache() -> GeneratorCache:
    return _default_cache
