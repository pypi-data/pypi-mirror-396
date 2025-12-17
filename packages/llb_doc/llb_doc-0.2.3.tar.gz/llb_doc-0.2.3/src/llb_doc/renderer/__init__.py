from ..core.block import Block
from ..core.document import Document


def render_block(block: Block) -> str:
    return block.render()


def render_document(doc: Document) -> str:
    return doc.render()


__all__ = ["render_block", "render_document"]
