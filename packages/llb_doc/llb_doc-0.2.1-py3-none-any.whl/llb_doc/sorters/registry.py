from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..core.block import Block

BlockSorter = Callable[[list["Block"]], list["Block"]]

SORTER_NAME_ATTR = "__llb_sorter_name__"


class SorterRegistry:
    """Registry for block sorters."""

    def __init__(self) -> None:
        self._sorters: dict[str, BlockSorter] = {}

    def register(self, name: str, func: BlockSorter) -> None:
        self._sorters[name] = func

    def get(self, name: str) -> BlockSorter | None:
        return self._sorters.get(name)

    def apply(self, blocks: list[Block], order: str) -> list[Block]:
        sorter = self.get(order)
        if sorter is None:
            raise ValueError(f"Unknown sorter: {order}")
        return sorter(blocks)


def block_sorter(name: str):
    """Decorator to mark a function as a block sorter."""

    def decorator(func: BlockSorter) -> BlockSorter:
        setattr(func, SORTER_NAME_ATTR, name)
        return func

    return decorator


def get_sorter_name(func: BlockSorter) -> str | None:
    return getattr(func, SORTER_NAME_ATTR, None)
