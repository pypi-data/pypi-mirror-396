from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.document import Document

from ..core.block import Block

BLOCK_START_RE = re.compile(r"^@block\s+(\S+)\s+(\S+)(?:\s+(\S+))?$")
BLOCK_END_RE = re.compile(r"^@end\s+(\S+)$")
META_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)=(.*)$")
SEPARATOR = "---"


class ParseError(ValueError):
    """Raised when LLB text cannot be parsed."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        if line_number is not None:
            message = f"Line {line_number}: {message}"
        super().__init__(message)
        self.line_number = line_number


def parse_llb(text: str) -> Document:
    """Parse LLB format text into a Document object."""
    from ..core.document import Document

    doc = Document()
    lines = text.split("\n")

    # Find separator positions
    separator_indices = [i for i, line in enumerate(lines) if line == SEPARATOR]

    # Determine prefix/body/suffix boundaries based on content detection
    # Find the last separator followed by @block (body start)
    # Find the first separator preceded by @end (body end)
    def find_first_nonblank_after(idx: int) -> str | None:
        """Find first non-blank line after given index."""
        for i in range(idx + 1, len(lines)):
            if lines[i].strip():
                return lines[i]
        return None

    def find_last_nonblank_before(idx: int) -> str | None:
        """Find last non-blank line before given index."""
        for i in range(idx - 1, -1, -1):
            if lines[i].strip():
                return lines[i]
        return None

    if len(separator_indices) == 0:
        # No separators: entire text is body (blocks only)
        prefix_end = 0
        body_start = 0
        body_end = len(lines)
        suffix_start = len(lines)
    else:
        # Find last separator followed by @block (body start boundary)
        body_start_sep = None
        for sep_idx in reversed(separator_indices):
            next_line = find_first_nonblank_after(sep_idx)
            if next_line and BLOCK_START_RE.match(next_line):
                body_start_sep = sep_idx
                break

        # Find first separator preceded by @end (body end boundary)
        body_end_sep = None
        for sep_idx in separator_indices:
            prev_line = find_last_nonblank_before(sep_idx)
            if prev_line and BLOCK_END_RE.match(prev_line):
                body_end_sep = sep_idx
                break

        if body_start_sep is not None and body_end_sep is not None:
            # prefix---body---suffix
            prefix_end = body_start_sep
            body_start = body_start_sep + 1
            body_end = body_end_sep
            suffix_start = body_end_sep + 1
        elif body_start_sep is not None:
            # prefix---body (no suffix)
            prefix_end = body_start_sep
            body_start = body_start_sep + 1
            body_end = len(lines)
            suffix_start = len(lines)
        elif body_end_sep is not None:
            # body---suffix (no prefix)
            prefix_end = 0
            body_start = 0
            body_end = body_end_sep
            suffix_start = body_end_sep + 1
        else:
            # No valid boundaries found, treat entire content as body
            prefix_end = 0
            body_start = 0
            body_end = len(lines)
            suffix_start = len(lines)

    # Extract prefix
    if prefix_end > 0:
        prefix_text = "\n".join(lines[:prefix_end])
        # Remove leading/trailing empty lines from join boundaries
        doc._prefix = prefix_text.rstrip("\n")

    # Extract suffix
    if suffix_start < len(lines):
        suffix_text = "\n".join(lines[suffix_start:])
        doc._suffix = suffix_text.lstrip("\n")

    # Parse blocks in body section
    i = body_start
    while i < body_end:
        line = lines[i]

        # Skip empty lines between blocks
        if not line.strip():
            i += 1
            continue

        match = BLOCK_START_RE.match(line)
        if not match:
            raise ParseError(f"Expected @block, got: {line!r}", line_number=i + 1)

        block_id, block_type, lang = match.groups()
        meta: dict[str, str] = {}
        content_lines: list[str] = []
        i += 1

        # Parse metadata lines
        while i < body_end and lines[i].strip():
            meta_match = META_RE.match(lines[i])
            if meta_match:
                key, value = meta_match.groups()
                meta[key] = value
                i += 1
            else:
                break

        # Skip empty line after metadata
        if i < body_end and lines[i] == "":
            i += 1

        # Parse content until @end
        end_pattern = f"@end {block_id}"
        found_end = False
        while i < body_end:
            if lines[i] == end_pattern:
                found_end = True
                break
            content_lines.append(lines[i])
            i += 1

        if not found_end:
            raise ParseError(f"Missing @end for block '{block_id}'")

        block = Block(
            id=block_id,
            type=block_type,
            lang=lang,
            meta=meta,
            content="\n".join(content_lines).rstrip("\n"),
            _doc=doc,
        )
        doc._block_order.append(block_id)
        doc._id_index[block_id] = block
        i += 1

    return doc
