"""Tests for llb_doc library."""

import pytest

from llb_doc import Block, Document, ParseError, create_llb, parse_llb
from llb_doc.core.document import BlockNotFoundError, DuplicateIDError, MetaRefreshMode


class TestBlock:
    def test_block_creation(self):
        block = Block(id="b1", type="ticket", content="Test content")
        assert block.type == "ticket"
        assert block.content == "Test content"
        assert block.lang is None
        assert block.meta == {}

    def test_block_with_lang(self):
        block = Block(id="b2", type="code", content="print('hello')", lang="python")
        assert block.lang == "python"

    def test_block_with_meta(self):
        block = Block(id="b3", type="note", content="content", meta={"source": "test", "priority": "high"})
        assert block.meta["source"] == "test"
        assert block.meta["priority"] == "high"

    def test_block_with_kwargs(self):
        block = Block(id="b4", type="log", content="error", level="error", service="api")
        assert block.meta["level"] == "error"
        assert block.meta["service"] == "api"

    def test_block_kwargs_merge_with_meta(self):
        block = Block(id="b5", type="note", meta={"existing": "value"}, author="alice", status="open")
        assert block.meta["existing"] == "value"
        assert block.meta["author"] == "alice"
        assert block.meta["status"] == "open"

    def test_block_equality(self):
        block1 = Block(id="b1", type="note", content="test", lang="en", source="a")
        block2 = Block(id="b1", type="note", content="test", lang="en", source="a")
        block3 = Block(id="b1", type="note", content="different")
        assert block1 == block2
        assert block1 != block3

    def test_block_repr(self):
        block = Block(id="b1", type="note", content="test")
        assert "Block(" in repr(block)
        assert "id='b1'" in repr(block)


class TestDocument:
    def test_create_empty_document(self):
        doc = create_llb()
        assert isinstance(doc, Document)
        assert len(doc.blocks) == 0

    def test_add_block(self):
        doc = create_llb()
        doc.add_block("ticket", "Test content", lang="en", source="jira")
        assert len(doc.blocks) == 1
        assert doc.blocks[0].type == "ticket"
        assert doc.blocks[0].content == "Test content"

    def test_fluent_api(self):
        doc = create_llb()
        doc.block("api", lang="json").meta(source="test").content('{"key": "value"}').add()
        assert len(doc.blocks) == 1
        assert doc.blocks[0].type == "api"

    def test_context_manager(self):
        doc = create_llb()
        with doc.block("note", "zh") as b:
            b.source = "review"
            b.content = "测试内容"
        assert len(doc.blocks) == 1
        assert doc.blocks[0].lang == "zh"


class TestRenderAndParse:
    def test_render_produces_string(self):
        doc = create_llb()
        doc.add_block("test", "content")
        result = doc.render()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parse_roundtrip(self):
        doc = create_llb()
        doc.add_block("ticket", "User cannot login", lang="en", source="jira")
        doc.add_block("note", "需要检查认证逻辑", lang="zh", source="review")
        
        rendered = doc.render()
        parsed = parse_llb(rendered)
        
        assert len(parsed.blocks) == len(doc.blocks)
        for orig, parsed_block in zip(doc.blocks, parsed.blocks):
            assert orig.type == parsed_block.type
            assert orig.content == parsed_block.content
            assert orig.lang == parsed_block.lang

    def test_empty_document_render(self):
        doc = create_llb()
        result = doc.render()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_arender_produces_string(self):
        doc = create_llb()
        doc.add_block("test", "content")
        result = await doc.arender()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_arender_matches_sync(self):
        doc = create_llb()
        doc.add_block("ticket", "User cannot login", lang="en")
        sync_result = doc.render(meta_refresh=MetaRefreshMode.NONE)
        async_result = await doc.arender(meta_refresh=MetaRefreshMode.NONE)
        assert sync_result == async_result


class TestPrefixSuffix:
    def test_prefix_only(self):
        doc = create_llb()
        doc.prefix = "This is the prefix"
        doc.add_block("test", "content")
        rendered = doc.render()
        assert rendered.startswith("This is the prefix")
        parsed = parse_llb(rendered)
        assert parsed.prefix == "This is the prefix"

    def test_suffix_only(self):
        doc = create_llb()
        doc.suffix = "--- END ---"
        doc.add_block("test", "content")
        rendered = doc.render()
        assert rendered.endswith("--- END ---")
        parsed = parse_llb(rendered)
        assert parsed.suffix == "--- END ---"

    def test_prefix_and_suffix(self):
        doc = create_llb()
        doc.prefix = "Header text"
        doc.suffix = "Footer text"
        doc.add_block("test", "content")
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert parsed.prefix == "Header text"
        assert parsed.suffix == "Footer text"
        assert len(parsed.blocks) == 1

    def test_prefix_suffix_roundtrip(self):
        doc = create_llb()
        doc.prefix = "Multi\nline\nprefix"
        doc.suffix = "Multi\nline\nsuffix"
        doc.add_block("note", "content", lang="en")
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert parsed == doc

    def test_prefix_with_whitespace_preserved(self):
        """Whitespace in prefix/suffix should be preserved after roundtrip."""
        doc = create_llb()
        doc.prefix = "  indented prefix  "
        doc.suffix = "  indented suffix  "
        doc.add_block("test", "content")
        parsed = parse_llb(doc.render())
        assert parsed.prefix == doc.prefix
        assert parsed.suffix == doc.suffix
        assert parsed == doc

    def test_complex_prefix_roundtrip(self):
        """Complex multiline prefix with code blocks should roundtrip correctly."""
        doc = create_llb()
        doc.block("ticket", lang="en").meta(source="jira", priority="high").content(
            "User cannot upload files larger than 10MB"
        ).add()
        with doc.block("api", "json") as b:
            b.source = "storage_service"
            b.content = '{"max_size": 5242880, "unit": "bytes"}'
        doc.add_block("note", "前端限制与后端配置不一致", source="code_review", lang="zh")

        doc.prefix = """Each block follows this structure:
```
@block <id> <type> [lang]
key1=value1
key2=value2

<content>

@end <id>
```"""
        parsed = parse_llb(doc.render())
        assert parsed == doc

    def test_empty_prefix_suffix(self):
        doc = create_llb()
        doc.add_block("test", "content")
        assert doc.prefix == ""
        assert doc.suffix == ""

    def test_document_equality_with_prefix_suffix(self):
        doc1 = create_llb()
        doc1.prefix = "prefix"
        doc1.suffix = "suffix"
        doc1.add_block("test", "content")

        doc2 = create_llb()
        doc2.prefix = "prefix"
        doc2.suffix = "suffix"
        doc2.add_block("test", "content")

        doc3 = create_llb()
        doc3.prefix = "different"
        doc3.suffix = "suffix"
        doc3.add_block("test", "content")

        assert doc1 == doc2
        assert doc1 != doc3


class TestEdgeCases:
    def test_special_characters_in_content(self):
        doc = create_llb()
        special_content = "Line1\nLine2\n<tag>value</tag>"
        doc.add_block("test", special_content)
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert parsed.blocks[0].content == special_content

    def test_unicode_content(self):
        doc = create_llb()
        doc.add_block("note", "中文内容 日本語 한국어 🎉", lang="multi")
        rendered = doc.render()
        parsed = parse_llb(rendered)
        assert "中文内容" in parsed.blocks[0].content

    def test_multiple_meta_fields(self):
        doc = create_llb()
        doc.add_block(
            "log",
            "Error occurred",
            level="error",
            timestamp="2024-01-15T10:30:00Z",
            service="api",
        )
        assert len(doc.blocks[0].meta) == 3


class TestParseError:
    def test_missing_end_marker(self):
        """Parser should raise ParseError when @end is missing."""
        invalid_text = "@block b1 test\n\ncontent without end"
        with pytest.raises(ParseError, match="Missing @end"):
            parse_llb(invalid_text)

    def test_invalid_block_start_in_body(self):
        """Parser should raise ParseError for invalid lines in body section."""
        invalid_text = "not a valid block line"
        with pytest.raises(ParseError, match="Expected @block"):
            parse_llb(invalid_text)

    def test_multiple_separators_in_prefix_suffix(self):
        """Parser should detect body boundaries even with extra separators."""
        # Extra separators in prefix and suffix areas
        text = "pre1\n---\npre2\n---\n@block b1 test\n\ncontent\n@end b1\n---\nsuf1\n---\nsuf2"
        doc = parse_llb(text)
        assert doc.prefix == "pre1\n---\npre2"
        assert doc["b1"].content == "content"
        assert doc.suffix == "suf1\n---\nsuf2"

    def test_multiple_separators_prefix_body_only(self):
        """Parser handles multiple separators with prefix+body (no suffix)."""
        text = "pre1\n---\npre2\n---\n@block b1 test\n\ncontent\n@end b1"
        doc = parse_llb(text)
        assert doc.prefix == "pre1\n---\npre2"
        assert doc["b1"].content == "content"
        assert doc.suffix == ""

    def test_multiple_separators_body_suffix_only(self):
        """Parser handles multiple separators with body+suffix (no prefix)."""
        text = "@block b1 test\n\ncontent\n@end b1\n---\nsuf1\n---\nsuf2"
        doc = parse_llb(text)
        assert doc.prefix == ""
        assert doc["b1"].content == "content"
        assert doc.suffix == "suf1\n---\nsuf2"

    def test_parse_error_includes_line_number(self):
        """ParseError should include line number when available."""
        invalid_text = "@block b1 test\n\ncontent\n\n@end b1\n\ninvalid line here"
        with pytest.raises(ParseError) as exc_info:
            parse_llb(invalid_text)
        assert exc_info.value.line_number is not None


class TestDocumentOperations:
    """Test Document dunder methods and operations."""

    def test_document_len(self):
        doc = create_llb()
        assert len(doc) == 0
        doc.add_block("note", "content1")
        assert len(doc) == 1
        doc.add_block("note", "content2")
        assert len(doc) == 2

    def test_document_contains(self):
        doc = create_llb()
        doc.add_block("note", "content", id_="b1")
        assert "b1" in doc
        assert "b2" not in doc

    def test_document_iter(self):
        doc = create_llb()
        doc.add_block("note", "content1", id_="b1")
        doc.add_block("note", "content2", id_="b2")
        blocks = list(doc)
        assert len(blocks) == 2
        assert blocks[0].id == "b1"
        assert blocks[1].id == "b2"

    def test_replace_block(self):
        doc = create_llb()
        doc.add_block("note", "old content", id_="b1", author="alice")
        doc.replace_block("b1", content="new content", status="done")
        block = doc["b1"]
        assert block.content == "new content"
        assert block.type == "note"
        assert block.meta["author"] == "alice"
        assert block.meta["status"] == "done"

    def test_replace_block_not_found(self):
        doc = create_llb()
        with pytest.raises(BlockNotFoundError):
            doc.replace_block("nonexistent", content="new")

    def test_set_block_create_new(self):
        doc = create_llb()
        block = doc.set_block("b1", "note", "content", author="bob")
        assert block.id == "b1"
        assert block.type == "note"
        assert block.content == "content"
        assert block.meta["author"] == "bob"

    def test_set_block_overwrite_existing(self):
        doc = create_llb()
        doc.add_block("note", "old", id_="b1", old_meta="value")
        doc.set_block("b1", "ticket", "new", new_meta="new_value")
        block = doc["b1"]
        assert block.type == "ticket"
        assert block.content == "new"
        assert "old_meta" not in block.meta
        assert block.meta["new_meta"] == "new_value"

    def test_reorder_blocks(self):
        doc = create_llb()
        doc.add_block("note", "c1", id_="b1")
        doc.add_block("note", "c2", id_="b2")
        doc.add_block("note", "c3", id_="b3")
        doc.reorder_blocks(["b3", "b1", "b2"])
        blocks = doc.blocks
        assert blocks[0].id == "b3"
        assert blocks[1].id == "b1"
        assert blocks[2].id == "b2"

    def test_reorder_blocks_missing_id(self):
        doc = create_llb()
        doc.add_block("note", "c1", id_="b1")
        doc.add_block("note", "c2", id_="b2")
        with pytest.raises(ValueError, match="Missing block IDs"):
            doc.reorder_blocks(["b1"])

    def test_reorder_blocks_extra_id(self):
        doc = create_llb()
        doc.add_block("note", "c1", id_="b1")
        with pytest.raises(BlockNotFoundError):
            doc.reorder_blocks(["b1", "b2"])


class TestDuplicateIDError:
    """Test DuplicateIDError in Document."""

    def test_duplicate_id_raises_error(self):
        doc = create_llb()
        doc.add_block("note", "content", id_="b1")
        with pytest.raises(DuplicateIDError):
            doc.add_block("note", "content2", id_="b1")

    def test_duplicate_id_error_message(self):
        doc = create_llb()
        doc.add_block("note", "content", id_="test_id")
        with pytest.raises(DuplicateIDError) as exc_info:
            doc.add_block("note", "content2", id_="test_id")
        assert "test_id" in str(exc_info.value)


class TestMetaRefreshMode:
    """Test MetaRefreshMode enum values."""

    def test_meta_refresh_mode_values(self):
        assert MetaRefreshMode.NONE.value == "none"
        assert MetaRefreshMode.NORMAL.value == "normal"
        assert MetaRefreshMode.FORCE.value == "force"

    def test_render_with_meta_refresh_none(self):
        doc = create_llb()
        doc.add_block("note", "content")
        result = doc.render(meta_refresh=MetaRefreshMode.NONE)
        assert isinstance(result, str)
