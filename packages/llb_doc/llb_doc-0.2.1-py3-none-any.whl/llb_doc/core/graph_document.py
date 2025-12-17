from __future__ import annotations

import asyncio
from collections import deque
from typing import Self

from .block import Block
from .ctx import Ctx
from .document import Document, IDGenerator, MetaRefreshMode
from .edge import Edge
from .node import Node

from ..generators.registry import MetaGenerator
from ..sorters.registry import BlockSorter, block_sorter


class NodeNotFoundError(KeyError):
    """Raised when a node with the given ID is not found."""

    def __init__(self, id_: str) -> None:
        super().__init__(f"Node with ID '{id_}' not found")
        self.id = id_


class NodeBuilder:
    """Builder for creating nodes."""

    def __init__(self, doc: GraphDocument, type_: str, lang: str | None = None) -> None:
        self._doc = doc
        self._id: str | None = None
        self._type = type_
        self._lang = lang
        self._meta: dict[str, str] = {}
        self._content: str = ""

    def id(self, id_: str) -> Self:
        self._id = id_
        return self

    def meta(self, **kwargs: str) -> Self:
        self._meta.update(kwargs)
        return self

    def content(self, text: str) -> Self:
        self._content = text
        return self

    def add(self) -> Node:
        node_id = self._id or self._doc._generate_node_id()
        self._doc._validate_unique_node_id(node_id)
        node = Node(
            id=node_id,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            _doc=self._doc,
        )
        self._doc._node_order.append(node_id)
        self._doc._node_index[node_id] = node
        return node

    def __enter__(self) -> Node:
        node_id = self._id or self._doc._generate_node_id()
        self._doc._validate_unique_node_id(node_id)
        self._node = Node(
            id=node_id,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            _doc=self._doc,
        )
        return self._node

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self._doc._node_order.append(self._node.id)
            self._doc._node_index[self._node.id] = self._node


class EdgeBuilder:
    """Builder for creating edges."""

    def __init__(
        self,
        doc: GraphDocument,
        from_id: str,
        to_id: str,
        rel: str,
    ) -> None:
        self._doc = doc
        self._id: str | None = None
        self._from_id = from_id
        self._to_id = to_id
        self._rel = rel
        self._type: str = "edge"
        self._lang: str | None = None
        self._meta: dict[str, str] = {}
        self._content: str = ""
        self._render_edge: bool = True

    def id(self, id_: str) -> Self:
        self._id = id_
        return self

    def type(self, type_: str) -> Self:
        self._type = type_
        return self

    def lang(self, lang: str) -> Self:
        self._lang = lang
        return self

    def meta(self, **kwargs: str) -> Self:
        self._meta.update(kwargs)
        return self

    def content(self, text: str) -> Self:
        self._content = text
        return self

    def render_edge(self, render: bool) -> Self:
        self._render_edge = render
        return self

    def add(self) -> Edge:
        edge_id = self._id or self._doc._generate_edge_id()
        edge = Edge(
            id=edge_id,
            from_id=self._from_id,
            to_id=self._to_id,
            rel=self._rel,
            type=self._type,
            lang=self._lang,
            meta=self._meta,
            content=self._content,
            render_edge=self._render_edge,
            _doc=self._doc,
        )
        self._doc._edges.append(edge)
        self._doc._edge_index[edge_id] = edge
        return edge


@block_sorter("focus_last")
def _focus_last_sort(blocks: list[Block]) -> list[Block]:
    """ctx -> (tier desc: nodes + edges per tier) -> focus"""
    ctx_blocks: list[Ctx] = []
    focus_node: Node | None = None
    node_tiers: dict[str, int] = {}
    nodes_by_tier: dict[int, list[Node]] = {}
    edges: list[Edge] = []

    for b in blocks:
        if isinstance(b, Ctx):
            ctx_blocks.append(b)
        elif isinstance(b, Node):
            if b.tier == 0:
                focus_node = b
                node_tiers[b.id] = 0
            else:
                tier = b.tier or 0
                node_tiers[b.id] = tier
                if tier not in nodes_by_tier:
                    nodes_by_tier[tier] = []
                nodes_by_tier[tier].append(b)
        elif isinstance(b, Edge):
            edges.append(b)

    edges_by_tier: dict[int, list[Edge]] = {}
    for e in edges:
        from_tier = node_tiers.get(e.from_id, 0)
        to_tier = node_tiers.get(e.to_id, 0)
        edge_tier = max(from_tier, to_tier)
        if edge_tier not in edges_by_tier:
            edges_by_tier[edge_tier] = []
        edges_by_tier[edge_tier].append(e)

    result: list[Block] = []
    result.extend(ctx_blocks)

    all_tiers = sorted(set(nodes_by_tier.keys()) | set(edges_by_tier.keys()), reverse=True)
    for tier in all_tiers:
        if tier in nodes_by_tier:
            result.extend(nodes_by_tier[tier])
        if tier in edges_by_tier:
            result.extend(edges_by_tier[tier])

    if focus_node:
        result.append(focus_node)
    return result


@block_sorter("focus_first")
def _focus_first_sort(blocks: list[Block]) -> list[Block]:
    """ctx -> focus -> (tier asc: nodes + edges per tier)"""
    ctx_blocks: list[Ctx] = []
    focus_node: Node | None = None
    node_tiers: dict[str, int] = {}
    nodes_by_tier: dict[int, list[Node]] = {}
    edges: list[Edge] = []

    for b in blocks:
        if isinstance(b, Ctx):
            ctx_blocks.append(b)
        elif isinstance(b, Node):
            if b.tier == 0:
                focus_node = b
                node_tiers[b.id] = 0
            else:
                tier = b.tier or 0
                node_tiers[b.id] = tier
                if tier not in nodes_by_tier:
                    nodes_by_tier[tier] = []
                nodes_by_tier[tier].append(b)
        elif isinstance(b, Edge):
            edges.append(b)

    edges_by_tier: dict[int, list[Edge]] = {}
    for e in edges:
        from_tier = node_tiers.get(e.from_id, 0)
        to_tier = node_tiers.get(e.to_id, 0)
        edge_tier = max(from_tier, to_tier)
        if edge_tier not in edges_by_tier:
            edges_by_tier[edge_tier] = []
        edges_by_tier[edge_tier].append(e)

    result: list[Block] = []
    result.extend(ctx_blocks)

    if focus_node:
        result.append(focus_node)

    all_tiers = sorted(set(nodes_by_tier.keys()) | set(edges_by_tier.keys()))
    for tier in all_tiers:
        if tier in nodes_by_tier:
            result.extend(nodes_by_tier[tier])
        if tier in edges_by_tier:
            result.extend(edges_by_tier[tier])

    return result


@block_sorter("tier_asc")
def _tier_asc_sort(blocks: list[Block]) -> list[Block]:
    """ctx -> tier asc -> edges"""
    ctx_blocks: list[Ctx] = []
    node_blocks: list[Node] = []
    edge_blocks: list[Edge] = []

    for b in blocks:
        if isinstance(b, Ctx):
            ctx_blocks.append(b)
        elif isinstance(b, Edge):
            edge_blocks.append(b)
        elif isinstance(b, Node):
            node_blocks.append(b)

    node_blocks.sort(key=lambda n: n.tier or 0)

    result: list[Block] = []
    result.extend(ctx_blocks)
    result.extend(node_blocks)
    result.extend(edge_blocks)
    return result


@block_sorter("tier_desc")
def _tier_desc_sort(blocks: list[Block]) -> list[Block]:
    """ctx -> tier desc -> edges"""
    ctx_blocks: list[Ctx] = []
    node_blocks: list[Node] = []
    edge_blocks: list[Edge] = []

    for b in blocks:
        if isinstance(b, Ctx):
            ctx_blocks.append(b)
        elif isinstance(b, Edge):
            edge_blocks.append(b)
        elif isinstance(b, Node):
            node_blocks.append(b)

    node_blocks.sort(key=lambda n: -(n.tier or 0))

    result: list[Block] = []
    result.extend(ctx_blocks)
    result.extend(node_blocks)
    result.extend(edge_blocks)
    return result


GRAPH_SORTERS = [_focus_last_sort, _focus_first_sort, _tier_asc_sort, _tier_desc_sort]


class GraphDocument(Document):
    """Graph document with nodes, edges, and context."""

    def __init__(
        self,
        graph_id: str | None = None,
        generators: list[MetaGenerator] | None = None,
        sorters: list[BlockSorter] | None = None,
    ) -> None:
        all_sorters = list(GRAPH_SORTERS)
        if sorters:
            all_sorters.extend(sorters)
        super().__init__(generators, all_sorters)

        self.graph_id = graph_id
        self._node_id_gen = IDGenerator("N")
        self._edge_id_gen = IDGenerator("E")
        self._ctx_id_gen = IDGenerator("C")
        self._node_order: list[str] = []
        self._node_index: dict[str, Node] = {}
        self._edges: list[Edge] = []
        self._edge_index: dict[str, Edge] = {}

    def _generate_node_id(self) -> str:
        while True:
            id_ = self._node_id_gen.next()
            if id_ not in self._node_index:
                return id_

    def _generate_edge_id(self) -> str:
        while True:
            id_ = self._edge_id_gen.next()
            if id_ not in self._edge_index:
                return id_

    def _generate_ctx_id(self) -> str:
        return self._ctx_id_gen.next()

    def _validate_unique_node_id(self, id_: str) -> None:
        if id_ in self._node_index:
            from .document import DuplicateIDError

            raise DuplicateIDError(id_)

    @property
    def nodes(self) -> list[Node]:
        return [self._node_index[id_] for id_ in self._node_order]

    @property
    def edges(self) -> list[Edge]:
        return list(self._edges)

    def node(self, type_: str, lang: str | None = None) -> NodeBuilder:
        return NodeBuilder(self, type_, lang)

    def add_node(
        self,
        type_: str,
        content: str = "",
        *,
        lang: str | None = None,
        id_: str | None = None,
        **meta: str,
    ) -> Node:
        node_id = id_ or self._generate_node_id()
        self._validate_unique_node_id(node_id)
        node = Node(
            id=node_id,
            type=type_,
            lang=lang,
            meta=meta,
            content=content,
            _doc=self,
        )
        self._node_order.append(node_id)
        self._node_index[node_id] = node
        return node

    def get_node(self, id_: str) -> Node | None:
        return self._node_index.get(id_)

    def has_node(self, id_: str) -> bool:
        return id_ in self._node_index

    def remove_node(self, id_: str) -> Node:
        if id_ not in self._node_index:
            raise NodeNotFoundError(id_)
        node = self._node_index.pop(id_)
        self._node_order.remove(id_)
        node._doc = None
        self._edges = [e for e in self._edges if e.from_id != id_ and e.to_id != id_]
        self._edge_index = {
            k: v
            for k, v in self._edge_index.items()
            if v.from_id != id_ and v.to_id != id_
        }
        return node

    def edge(self, from_id: str, to_id: str, rel: str) -> EdgeBuilder:
        return EdgeBuilder(self, from_id, to_id, rel)

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        rel: str,
        *,
        type_: str = "edge",
        lang: str | None = None,
        id_: str | None = None,
        content: str = "",
        render_edge: bool = True,
        **meta: str,
    ) -> Edge:
        edge_id = id_ or self._generate_edge_id()
        edge = Edge(
            id=edge_id,
            from_id=from_id,
            to_id=to_id,
            rel=rel,
            type=type_,
            lang=lang,
            meta=meta,
            content=content,
            render_edge=render_edge,
            _doc=self,
        )
        self._edges.append(edge)
        self._edge_index[edge_id] = edge
        return edge

    def get_edge(self, id_: str) -> Edge | None:
        return self._edge_index.get(id_)

    def get_edges_from(self, node_id: str) -> list[Edge]:
        return [e for e in self._edges if e.from_id == node_id]

    def get_edges_to(self, node_id: str) -> list[Edge]:
        return [e for e in self._edges if e.to_id == node_id]

    def remove_edge(self, id_: str) -> Edge:
        if id_ not in self._edge_index:
            raise KeyError(f"Edge '{id_}' not found")
        edge = self._edge_index.pop(id_)
        self._edges.remove(edge)
        edge._doc = None
        return edge

    async def ensure_meta(self, *, force: bool = False) -> None:
        """Apply generators to all nodes and edges."""
        all_blocks: list[Block] = list(self.nodes) + list(self.edges)
        await asyncio.gather(
            *[self._generator_registry.apply(b, force=force) for b in all_blocks]
        )

    def _compute_tiers(
        self, focus: str, radius: int, strategy: str = "bfs"
    ) -> dict[str, int]:
        """Compute tier for each node using BFS from focus node."""
        if focus not in self._node_index:
            raise NodeNotFoundError(focus)

        tiers: dict[str, int] = {}
        if strategy == "bfs":
            queue: deque[tuple[str, int]] = deque([(focus, 0)])
            visited: set[str] = {focus}

            while queue:
                node_id, tier = queue.popleft()
                if tier > radius:
                    continue
                tiers[node_id] = tier

                for edge in self._edges:
                    next_id = None
                    if edge.from_id == node_id and edge.to_id not in visited:
                        next_id = edge.to_id
                    elif edge.to_id == node_id and edge.from_id not in visited:
                        next_id = edge.from_id
                    if next_id and next_id in self._node_index:
                        visited.add(next_id)
                        queue.append((next_id, tier + 1))
        return tiers

    def _fill_in_out_edges(self, included_nodes: set[str]) -> None:
        """Fill in_edges and out_edges for nodes within included set."""
        for node_id in included_nodes:
            node = self._node_index[node_id]
            node.in_edges = []
            node.out_edges = []

        for edge in self._edges:
            if edge.from_id in included_nodes and edge.to_id in included_nodes:
                from_node = self._node_index[edge.from_id]
                to_node = self._node_index[edge.to_id]
                from_node.out_edges.append(f"{edge.to_id}:{edge.rel}")
                to_node.in_edges.append(f"{edge.from_id}:{edge.rel}")

    def _build_tiers_string(self, tiers: dict[str, int]) -> str:
        """Build tiers string like '0:N42;1:N10,N50'."""
        tier_groups: dict[int, list[str]] = {}
        for node_id, tier in tiers.items():
            if tier not in tier_groups:
                tier_groups[tier] = []
            tier_groups[tier].append(node_id)

        parts = []
        for tier in sorted(tier_groups.keys()):
            nodes = ",".join(sorted(tier_groups[tier]))
            parts.append(f"{tier}:{nodes}")
        return ";".join(parts)

    def render(
        self,
        *,
        focus: str | None = None,
        radius: int = 1,
        strategy: str = "bfs",
        order: str | None = "focus_last",
        ctx_content: str = "",
        ctx_meta: dict[str, str] | None = None,
        meta_refresh: MetaRefreshMode = MetaRefreshMode.NORMAL,
    ) -> str:
        """Render graph document with context."""
        if meta_refresh != MetaRefreshMode.NONE:
            force = meta_refresh == MetaRefreshMode.FORCE
            asyncio.run(self.ensure_meta(force=force))

        if focus is None:
            return self._render_all_nodes(order=order)

        tiers = self._compute_tiers(focus, radius, strategy)
        included_nodes = set(tiers.keys())

        for node_id, tier in tiers.items():
            self._node_index[node_id].tier = tier

        self._fill_in_out_edges(included_nodes)

        tiers_str = self._build_tiers_string(tiers)

        ctx = Ctx(
            id=self._generate_ctx_id(),
            focus=focus,
            radius=radius,
            strategy=strategy,
            tiers=tiers_str,
            content=ctx_content,
            meta=ctx_meta or {},
            _doc=self,
        )

        included_edges = [
            e
            for e in self._edges
            if e.from_id in included_nodes
            and e.to_id in included_nodes
            and e.render_edge
        ]

        blocks: list[Block] = [ctx]
        blocks.extend(self._node_index[nid] for nid in included_nodes)
        blocks.extend(included_edges)

        sorted_blocks = self._sorter_registry.apply(blocks, order or "focus_last")

        rendered_blocks = [b.render() for b in sorted_blocks]
        body = "\n\n".join(rendered_blocks)

        parts: list[str] = []
        if self._prefix:
            parts.append(self._prefix)
            parts.append("---")
        if body:
            parts.append(body)
        if self._suffix:
            parts.append("---")
            parts.append(self._suffix)
        return "\n\n".join(parts)

    def _render_all_nodes(
        self,
        *,
        order: str | None = None,
    ) -> str:
        """Render all nodes without focus/radius filtering."""
        all_node_ids = set(self._node_order)
        self._fill_in_out_edges(all_node_ids)

        blocks: list[Block] = list(self.nodes)
        blocks.extend(e for e in self._edges if e.render_edge)

        if order:
            try:
                blocks = self._sorter_registry.apply(blocks, order)
            except ValueError:
                pass

        rendered_blocks = [b.render() for b in blocks]
        body = "\n\n".join(rendered_blocks)

        parts: list[str] = []
        if self._prefix:
            parts.append(self._prefix)
            parts.append("---")
        if body:
            parts.append(body)
        if self._suffix:
            parts.append("---")
            parts.append(self._suffix)
        return "\n\n".join(parts)


def create_graph(
    graph_id: str | None = None,
    *,
    generators: list[MetaGenerator] | None = None,
    sorters: list[BlockSorter] | None = None,
) -> GraphDocument:
    return GraphDocument(graph_id, generators, sorters)
