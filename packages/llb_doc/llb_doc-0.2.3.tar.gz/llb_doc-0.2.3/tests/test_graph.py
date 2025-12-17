"""Tests for GraphDocument and graph rendering."""

import pytest

from llb_doc import NodeNotFoundError, create_graph
from llb_doc.core import Ctx, Edge, Node


class TestGraphDocumentBasic:
    """Test basic GraphDocument functionality."""

    def test_create_graph(self):
        g = create_graph("test-graph")
        assert g.graph_id == "test-graph"
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_add_node(self):
        g = create_graph()
        node = g.add_node("person", "Alice content", name="Alice")
        assert node.id == "N1"
        assert node.type == "person"
        assert node.content == "Alice content"
        assert node.meta["name"] == "Alice"
        assert len(g.nodes) == 1

    def test_add_node_with_custom_id(self):
        g = create_graph()
        node = g.add_node("person", id_="custom-node")
        assert node.id == "custom-node"

    def test_node_builder(self):
        g = create_graph()
        node = g.node("person").id("N99").meta(name="Bob").content("Bob content").add()
        assert node.id == "N99"
        assert node.type == "person"
        assert node.meta["name"] == "Bob"

    def test_node_builder_context(self):
        g = create_graph()
        with g.node("person").id("N100") as node:
            node.content = "Context content"
            node.meta["role"] = "admin"
        assert g.has_node("N100")
        assert g.get_node("N100").content == "Context content"

    def test_get_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        assert g.get_node("N1") is not None
        assert g.get_node("N999") is None

    def test_has_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        assert g.has_node("N1")
        assert not g.has_node("N999")

    def test_remove_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        removed = g.remove_node("N1")
        assert removed.id == "N1"
        assert not g.has_node("N1")
        assert len(g.edges) == 0  # Edge should be removed too


class TestGraphDocumentEdges:
    """Test edge operations."""

    def test_add_edge(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        edge = g.add_edge("N1", "N2", "knows", weight="5")
        assert edge.id == "E1"
        assert edge.from_id == "N1"
        assert edge.to_id == "N2"
        assert edge.rel == "knows"
        assert edge.meta["weight"] == "5"

    def test_edge_builder(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        edge = g.edge("N1", "N2", "knows").meta(since="2020").add()
        assert edge.rel == "knows"
        assert edge.meta["since"] == "2020"

    def test_get_edge(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1")
        assert g.get_edge("E1") is not None
        assert g.get_edge("E999") is None

    def test_get_edges_from(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N1", "N3", "knows")
        g.add_edge("N2", "N3", "knows")
        edges = g.get_edges_from("N1")
        assert len(edges) == 2

    def test_get_edges_to(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N3", "knows")
        g.add_edge("N2", "N3", "knows")
        edges = g.get_edges_to("N3")
        assert len(edges) == 2

    def test_remove_edge(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1")
        g.remove_edge("E1")
        assert g.get_edge("E1") is None
        assert len(g.edges) == 0


class TestTierComputation:
    """Test tier computation (BFS)."""

    def test_single_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        tiers = g._compute_tiers("N1", radius=1)
        assert tiers == {"N1": 0}

    def test_linear_chain(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        tiers = g._compute_tiers("N1", radius=2)
        assert tiers == {"N1": 0, "N2": 1, "N3": 2}

    def test_radius_limit(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        tiers = g._compute_tiers("N1", radius=1)
        assert tiers == {"N1": 0, "N2": 1}
        assert "N3" not in tiers

    def test_bidirectional_edges(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        tiers_from_n1 = g._compute_tiers("N1", radius=1)
        tiers_from_n2 = g._compute_tiers("N2", radius=1)
        assert tiers_from_n1 == {"N1": 0, "N2": 1}
        assert tiers_from_n2 == {"N2": 0, "N1": 1}

    def test_focus_not_found(self):
        g = create_graph()
        with pytest.raises(NodeNotFoundError):
            g._compute_tiers("N999", radius=1)


class TestInOutFilling:
    """Test in_edges/out_edges auto-fill."""

    def test_fill_in_out_edges(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")
        g._fill_in_out_edges({"N1", "N2", "N3"})
        n1 = g.get_node("N1")
        n2 = g.get_node("N2")
        n3 = g.get_node("N3")
        assert n1.out_edges == ["N2:knows"]
        assert n1.in_edges == []
        assert n2.out_edges == ["N3:knows"]
        assert n2.in_edges == ["N1:knows"]
        assert n3.out_edges == []
        assert n3.in_edges == ["N2:knows"]

    def test_fill_partial_set(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")
        g._fill_in_out_edges({"N1", "N2"})
        n1 = g.get_node("N1")
        n2 = g.get_node("N2")
        assert n1.out_edges == ["N2:knows"]
        assert n2.in_edges == ["N1:knows"]
        assert n2.out_edges == []  # N3 not in set


class TestTiersString:
    """Test tiers string building."""

    def test_build_tiers_string(self):
        g = create_graph()
        tiers = {"N1": 0, "N2": 1, "N3": 1}
        result = g._build_tiers_string(tiers)
        assert "0: N1" in result
        assert "1:" in result
        assert "N2" in result
        assert "N3" in result

    def test_build_tiers_string_sorted(self):
        g = create_graph()
        tiers = {"N3": 2, "N1": 0, "N2": 1}
        result = g._build_tiers_string(tiers)
        lines = result.split("\n")
        assert lines[0].startswith("0:")
        assert lines[1].startswith("1:")
        assert lines[2].startswith("2:")


class TestGraphRender:
    """Test graph rendering."""

    def test_render_without_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = g.render()
        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "@edge E1 N1 -> N2 knows" in output

    def test_render_with_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_node("person", "Carol", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")
        output = g.render(focus="N1", radius=1)
        assert "@ctx" in output
        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "N3" not in output  # Outside radius

    def test_render_focus_last(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = g.render(focus="N1", radius=1, order="focus_last")
        lines = output.split("\n")
        ctx_line = next(i for i, line in enumerate(lines) if "@ctx" in line)
        focus_line = next(i for i, line in enumerate(lines) if "@node N1" in line)
        assert ctx_line < focus_line  # ctx before focus

    def test_render_focus_first(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = g.render(focus="N1", radius=1, order="focus_first")
        lines = output.split("\n")
        ctx_idx = next(i for i, line in enumerate(lines) if "@ctx" in line)
        focus_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        assert ctx_idx < focus_idx < n2_idx

    def test_render_with_ctx_content(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        output = g.render(focus="N1", radius=0, ctx_content="Context info")
        assert "Context info" in output

    def test_render_edge_hidden(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows", render_edge=False)
        output = g.render(focus="N1", radius=1)
        assert "@edge" not in output

    def test_render_prefix_suffix(self):
        g = create_graph()
        g.prefix = "# Graph Document"
        g.suffix = "# End"
        g.add_node("person", id_="N1")
        output = g.render(focus="N1", radius=0)
        assert output.startswith("# Graph Document")
        assert output.endswith("# End")


class TestGraphRenderAsync:
    """Test async graph rendering."""

    @pytest.mark.asyncio
    async def test_render_async_without_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = await g.arender()
        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "@edge E1 N1 -> N2 knows" in output

    @pytest.mark.asyncio
    async def test_render_async_with_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = await g.arender(focus="N1", radius=1)
        assert "@ctx" in output
        assert "@node N1 person" in output
        assert "@node N2 person" in output


class TestSorterStrategies:
    """Test different sorting strategies."""

    def test_tier_asc(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        output = g.render(focus="N1", radius=2, order="tier_asc")
        lines = output.split("\n")
        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        n3_idx = next(i for i, line in enumerate(lines) if "@node N3" in line)
        assert n1_idx < n2_idx < n3_idx

    def test_tier_desc(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        output = g.render(focus="N1", radius=2, order="tier_desc")
        lines = output.split("\n")
        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        n3_idx = next(i for i, line in enumerate(lines) if "@node N3" in line)
        assert n3_idx < n2_idx < n1_idx


class TestDuplicateID:
    """Test duplicate ID handling."""

    def test_duplicate_node_id(self):
        from llb_doc.core.document import DuplicateIDError

        g = create_graph()
        g.add_node("person", id_="N1")
        with pytest.raises(DuplicateIDError):
            g.add_node("person", id_="N1")


class TestNode:
    """Test Node block rendering and properties."""

    def test_render_header(self) -> None:
        node = Node(id="N1", type="person")
        assert node.render_header() == "@node N1 person"

    def test_render_header_with_lang(self) -> None:
        node = Node(id="N2", type="code", lang="python")
        assert node.render_header() == "@node N2 code python"

    def test_render_full(self) -> None:
        node = Node(id="N1", type="person", content="Alice")
        result = node.render()
        assert "@node N1 person" in result
        assert "Alice" in result
        assert "@end N1" in result

    def test_tier_and_edges(self) -> None:
        node = Node(id="N1", type="person")
        node.tier = 0
        node.in_edges = ["N2:knows"]
        node.out_edges = ["N3:likes"]
        assert node.tier == 0
        assert node.in_edges == ["N2:knows"]
        assert node.out_edges == ["N3:likes"]

    def test_meta_access(self) -> None:
        node = Node(id="N1", type="person", name="Alice")
        assert node.name == "Alice"


class TestEdge:
    """Test Edge block rendering and properties."""

    def test_render_header(self) -> None:
        edge = Edge(id="E1", from_id="N1", to_id="N2", rel="knows")
        assert edge.render_header() == "@edge E1 N1 -> N2 knows"

    def test_render_header_with_lang(self) -> None:
        edge = Edge(id="E2", from_id="N1", to_id="N2", rel="refs", lang="json")
        assert edge.render_header() == "@edge E2 N1 -> N2 refs json"

    def test_render_full(self) -> None:
        edge = Edge(id="E1", from_id="N1", to_id="N2", rel="knows", content="since 2020")
        result = edge.render()
        assert "@edge E1 N1 -> N2 knows" in result
        assert "since 2020" in result
        assert "@end E1" in result

    def test_render_edge_flag(self) -> None:
        edge = Edge(id="E1", from_id="N1", to_id="N2", rel="knows", render_edge=False)
        assert edge.render_edge is False


class TestCtx:
    """Test Ctx block rendering and properties."""

    def test_render_header(self) -> None:
        ctx = Ctx(id="C1")
        assert ctx.render_header() == "@ctx C1"

    def test_render_full(self) -> None:
        ctx = Ctx(id="C1", content="context info")
        result = ctx.render()
        assert "@ctx C1" in result
        assert "context info" in result
        assert "@end C1" in result

    def test_focus_and_radius(self) -> None:
        ctx = Ctx(id="C1", focus="N42", radius=2, strategy="bfs", tiers="0:N42;1:N10")
        assert ctx.focus == "N42"
        assert ctx.radius == 2
        assert ctx.strategy == "bfs"
        assert ctx.tiers == "0:N42;1:N10"
