"""Tests for block sorters."""

import pytest

from llb_doc import Block, block_sorter, create_llb


@block_sorter("by_ts")
def sort_by_timestamp(blocks: list[Block]) -> list[Block]:
    return sorted(blocks, key=lambda b: b.meta.get("ts", ""))


@block_sorter("by_priority")
def sort_by_priority(blocks: list[Block]) -> list[Block]:
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(blocks, key=lambda b: priority_order.get(b.meta.get("priority", ""), 99))


@block_sorter("reverse")
def sort_reverse(blocks: list[Block]) -> list[Block]:
    return list(reversed(blocks))


class TestBlockSorter:
    def test_sorter_decorator_sets_attribute(self):
        from llb_doc.sorters import get_sorter_name

        assert get_sorter_name(sort_by_timestamp) == "by_ts"
        assert get_sorter_name(sort_by_priority) == "by_priority"

    def test_sorter_not_decorated_raises(self):
        def plain_sorter(blocks: list[Block]) -> list[Block]:
            return blocks

        with pytest.raises(ValueError, match="not decorated with @block_sorter"):
            create_llb(sorters=[plain_sorter])

    def test_render_without_order(self):
        doc = create_llb(sorters=[sort_by_timestamp])
        doc.add_block("email", "First", ts="2025-12-02")
        doc.add_block("log", "Second", ts="2025-12-01")
        rendered = doc.render()
        assert rendered.index("First") < rendered.index("Second")

    def test_render_with_order_by_ts(self):
        doc = create_llb(sorters=[sort_by_timestamp])
        doc.add_block("email", "First", ts="2025-12-02")
        doc.add_block("log", "Second", ts="2025-12-01")
        rendered = doc.render(order="by_ts")
        assert rendered.index("Second") < rendered.index("First")

    def test_render_with_order_by_priority(self):
        doc = create_llb(sorters=[sort_by_priority])
        doc.add_block("task", "Low priority task", priority="low")
        doc.add_block("task", "High priority task", priority="high")
        doc.add_block("task", "Medium priority task", priority="medium")
        rendered = doc.render(order="by_priority")
        assert rendered.index("High") < rendered.index("Medium") < rendered.index("Low")

    def test_render_with_multiple_sorters(self):
        doc = create_llb(sorters=[sort_by_timestamp, sort_by_priority])
        doc.add_block("a", "AAA", ts="2025-12-02", priority="low")
        doc.add_block("b", "BBB", ts="2025-12-01", priority="high")

        by_ts = doc.render(order="by_ts")
        assert by_ts.index("BBB") < by_ts.index("AAA")

        by_priority = doc.render(order="by_priority")
        assert by_priority.index("BBB") < by_priority.index("AAA")

    def test_unknown_sorter_raises(self):
        doc = create_llb(sorters=[sort_by_timestamp])
        doc.add_block("test", "content")
        with pytest.raises(ValueError, match="Unknown sorter"):
            doc.render(order="nonexistent")

    def test_sort_does_not_modify_original_order(self):
        doc = create_llb(sorters=[sort_reverse])
        doc.add_block("a", "First")
        doc.add_block("b", "Second")
        doc.add_block("c", "Third")

        doc.render(order="reverse")
        ids = [b.id for b in doc.blocks]
        assert ids[0] != "c"


class TestSorterRegistry:
    def test_registry_get_nonexistent(self):
        from llb_doc.sorters import SorterRegistry

        registry = SorterRegistry()
        assert registry.get("nonexistent") is None

    def test_registry_register_and_apply(self):
        from llb_doc.sorters import SorterRegistry

        registry = SorterRegistry()
        registry.register("reverse", lambda blocks: list(reversed(blocks)))

        blocks = [
            Block(id="b1", type="test", content="first"),
            Block(id="b2", type="test", content="second"),
        ]
        sorted_blocks = registry.apply(blocks, "reverse")
        assert sorted_blocks[0].id == "b2"
        assert sorted_blocks[1].id == "b1"
