"""Tests for GeneratorCache."""

import asyncio

from llb_doc import Block
from llb_doc.cache.cache import GeneratorCache, get_default_cache
from llb_doc.generators.registry import GeneratorRegistry, meta_generator


class TestGeneratorCacheBasic:
    """Test GeneratorCache basic operations."""

    def test_get_set(self):
        cache = GeneratorCache()
        block = Block(id="b1", type="note", content="hello")
        cache.set(block, "summary", "cached value")
        assert cache.get(block, "summary") == "cached value"

    def test_get_miss(self):
        cache = GeneratorCache()
        block = Block(id="b1", type="note", content="hello")
        assert cache.get(block, "missing_key") is None

    def test_compute_key_consistency(self):
        cache = GeneratorCache()
        block = Block(id="b1", type="note", content="hello")
        key1 = cache._compute_key(block, "test")
        key2 = cache._compute_key(block, "test")
        assert key1 == key2

    def test_compute_key_different_content(self):
        cache = GeneratorCache()
        block1 = Block(id="b1", type="note", content="hello")
        block2 = Block(id="b1", type="note", content="world")
        key1 = cache._compute_key(block1, "test")
        key2 = cache._compute_key(block2, "test")
        assert key1 != key2

    def test_compute_key_different_meta_key(self):
        cache = GeneratorCache()
        block = Block(id="b1", type="note", content="hello")
        key1 = cache._compute_key(block, "summary")
        key2 = cache._compute_key(block, "title")
        assert key1 != key2

    def test_clear(self):
        cache = GeneratorCache()
        block = Block(id="b1", type="note", content="hello")
        cache.set(block, "key1", "value1")
        cache.set(block, "key2", "value2")
        assert len(cache) == 2
        cache.clear()
        assert len(cache) == 0

    def test_len(self):
        cache = GeneratorCache()
        assert len(cache) == 0
        block = Block(id="b1", type="note", content="hello")
        cache.set(block, "key1", "value1")
        assert len(cache) == 1
        cache.set(block, "key2", "value2")
        assert len(cache) == 2


class TestDefaultCache:
    """Test get_default_cache."""

    def test_get_default_cache(self):
        cache = get_default_cache()
        assert isinstance(cache, GeneratorCache)

    def test_default_cache_singleton(self):
        cache1 = get_default_cache()
        cache2 = get_default_cache()
        assert cache1 is cache2


class TestCacheWithRegistry:
    """Test cache integration with GeneratorRegistry."""

    def test_cache_hit_skips_generator(self):
        cache = GeneratorCache()
        registry = GeneratorRegistry(cache=cache)
        call_count = 0

        @meta_generator("label")
        def gen_label(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return "computed_label"

        registry.register("label", gen_label)
        block1 = Block(id="b1", type="note", content="same_content")
        asyncio.run(registry.apply(block1))
        assert call_count == 1
        assert block1.meta["label"] == "computed_label"

        block2 = Block(id="b2", type="note", content="same_content")
        asyncio.run(registry.apply(block2))
        assert call_count == 1
        assert block2.meta["label"] == "computed_label"

    def test_cache_miss_different_content(self):
        cache = GeneratorCache()
        registry = GeneratorRegistry(cache=cache)
        call_count = 0

        @meta_generator("label")
        def gen_label(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return f"label-{call_count}"

        registry.register("label", gen_label)
        block1 = Block(id="b1", type="note", content="content1")
        asyncio.run(registry.apply(block1))
        assert call_count == 1

        block2 = Block(id="b2", type="note", content="content2")
        asyncio.run(registry.apply(block2))
        assert call_count == 2

    def test_cache_stores_result(self):
        cache = GeneratorCache()
        registry = GeneratorRegistry(cache=cache)

        @meta_generator("tag")
        def gen_tag(block: Block) -> str:
            return "cached_tag"

        registry.register("tag", gen_tag)
        block = Block(id="b1", type="note", content="content")
        asyncio.run(registry.apply(block))

        block2 = Block(id="b2", type="note", content="content")
        cached_value = cache.get(block2, "tag")
        assert cached_value == "cached_tag"

    def test_force_bypasses_cache(self):
        cache = GeneratorCache()
        registry = GeneratorRegistry(cache=cache)
        call_count = 0

        @meta_generator("counter")
        def gen_counter(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return f"count-{call_count}"

        registry.register("counter", gen_counter)
        block = Block(id="b1", type="note", content="test")
        cache.set(block, "counter", "old-value")

        asyncio.run(registry.apply(block, force=True))
        assert call_count == 1
        assert block.meta["counter"] == "count-1"


class TestCacheWithGraphDocument:
    """Test cache integration with GraphDocument."""

    def test_graph_document_cache_works_for_nodes(self):
        from llb_doc import create_graph
        from llb_doc.core.document import MetaRefreshMode

        call_count = 0

        @meta_generator("label")
        def gen_label(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return f"label-{call_count}"

        g = create_graph(generators=[gen_label])
        g.add_node("concept", "Python", id_="python")
        g.add_node("concept", "Django", id_="django")

        g.render(meta_refresh=MetaRefreshMode.NORMAL)
        assert call_count == 2
        assert g.get_node("python").meta["label"] == "label-1"
        assert g.get_node("django").meta["label"] == "label-2"

    def test_graph_document_cache_works_for_edges(self):
        from llb_doc import create_graph
        from llb_doc.core.document import MetaRefreshMode

        call_count = 0

        @meta_generator("edge_label")
        def gen_edge_label(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return f"edge-{call_count}"

        g = create_graph(generators=[gen_edge_label])
        g.add_node("concept", "A", id_="a")
        g.add_node("concept", "B", id_="b")
        g.add_edge("a", "b", "relates_to")

        g.render(focus="a", radius=1, meta_refresh=MetaRefreshMode.NORMAL)
        assert call_count == 3

    def test_graph_document_cache_hit(self):
        from llb_doc import create_graph
        from llb_doc.cache.cache import GeneratorCache
        from llb_doc.core.document import MetaRefreshMode

        cache = GeneratorCache()
        call_count = 0

        @meta_generator("tag")
        def gen_tag(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return "cached_tag"

        g = create_graph(generators=[gen_tag])
        g._generator_registry.set_cache(cache)
        g.add_node("concept", "Same Content", id_="n1")
        g.add_node("concept", "Same Content", id_="n2")

        g.render(meta_refresh=MetaRefreshMode.NORMAL)
        assert call_count == 1
        assert g.get_node("n1").meta["tag"] == "cached_tag"
        assert g.get_node("n2").meta["tag"] == "cached_tag"

    def test_graph_document_meta_refresh_none(self):
        from llb_doc import create_graph
        from llb_doc.core.document import MetaRefreshMode

        call_count = 0

        @meta_generator("skip")
        def gen_skip(block: Block) -> str:
            nonlocal call_count
            call_count += 1
            return "should_not_run"

        g = create_graph(generators=[gen_skip])
        g.add_node("concept", "Test", id_="t1")

        g.render(meta_refresh=MetaRefreshMode.NONE)
        assert call_count == 0
        assert "skip" not in g.get_node("t1").meta
