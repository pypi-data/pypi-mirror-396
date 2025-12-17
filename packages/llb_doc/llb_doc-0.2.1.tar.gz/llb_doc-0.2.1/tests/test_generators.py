"""Tests for meta_generator and GeneratorRegistry."""

import asyncio

import pytest

from llb_doc import Block, create_llb
from llb_doc.generators.registry import (
    GeneratorRegistry,
    get_meta_key,
    meta_generator,
)


class TestMetaGeneratorDecorator:
    """Test @meta_generator decorator."""

    def test_decorator_sets_attribute(self):
        @meta_generator("summary")
        def gen_summary(block: Block) -> str:
            return "test summary"

        assert hasattr(gen_summary, "__llb_meta_key__")
        assert gen_summary.__llb_meta_key__ == "summary"

    def test_get_meta_key(self):
        @meta_generator("title")
        def gen_title(block: Block) -> str:
            return "title"

        assert get_meta_key(gen_title) == "title"

    def test_get_meta_key_undecorated(self):
        def plain_func(block: Block) -> str:
            return "value"

        assert get_meta_key(plain_func) is None


class TestGeneratorRegistry:
    """Test GeneratorRegistry operations."""

    def test_register_and_get(self):
        registry = GeneratorRegistry()

        @meta_generator("tag")
        def gen_tag(block: Block) -> str:
            return "tagged"

        registry.register("tag", gen_tag)
        assert registry.get("tag") is gen_tag
        assert registry.get("nonexistent") is None

    def test_apply_to_block(self):
        registry = GeneratorRegistry()

        @meta_generator("label")
        def gen_label(block: Block) -> str:
            return f"label-{block.type}"

        registry.register("label", gen_label)
        block = Block(id="b1", type="note", content="content")
        asyncio.run(registry.apply(block))
        assert block.meta["label"] == "label-note"

    def test_apply_skips_existing_meta(self):
        registry = GeneratorRegistry()

        @meta_generator("label")
        def gen_label(block: Block) -> str:
            return "new"

        registry.register("label", gen_label)
        block = Block(id="b1", type="note", content="", label="existing")
        asyncio.run(registry.apply(block))
        assert block.meta["label"] == "existing"

    def test_apply_force_overwrites_meta(self):
        registry = GeneratorRegistry()

        @meta_generator("label")
        def gen_label(block: Block) -> str:
            return "forced"

        registry.register("label", gen_label)
        block = Block(id="b1", type="note", content="", label="old")
        asyncio.run(registry.apply(block, force=True))
        assert block.meta["label"] == "forced"

    def test_apply_all(self):
        registry = GeneratorRegistry()

        @meta_generator("status")
        def gen_status(block: Block) -> str:
            return "processed"

        registry.register("status", gen_status)
        doc = create_llb()
        doc.add_block("note", "c1", id_="b1")
        doc.add_block("note", "c2", id_="b2")
        asyncio.run(registry.apply_all(doc))
        assert doc["b1"].meta["status"] == "processed"
        assert doc["b2"].meta["status"] == "processed"

    def test_async_generator(self):
        registry = GeneratorRegistry()

        @meta_generator("async_label")
        async def gen_async(block: Block) -> str:
            return f"async-{block.id}"

        registry.register("async_label", gen_async)
        block = Block(id="b1", type="note", content="")
        asyncio.run(registry.apply(block))
        assert block.meta["async_label"] == "async-b1"


class TestUndecoratedFunctionError:
    """Test error when registering undecorated functions in Document."""

    def test_undecorated_function_raises_error(self):
        def plain_generator(block: Block) -> str:
            return "value"

        with pytest.raises(ValueError, match="not decorated with @meta_generator"):
            create_llb(generators=[plain_generator])
