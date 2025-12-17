"""Utility functions for working with spanning trees and graph partitions.

This module provides core operations for spanning trees including:
- Aggregating values over tree edges in both directions
- Computing closures when edges are cut
- Finding boundary nodes and edges between node sets
"""

from typing import Callable, Iterator, Hashable

from networkx import Graph, dfs_edges, edge_bfs

from partigraph.ust import random_spanning_tree

Node = Hashable
Edge = tuple[Node, Node]


def aggregate[V](
    tree: Graph,
    get: Callable[[Node], V],
    combine: Callable[[V, V], V],
) -> dict[Edge, V]:
    """Aggregate values over all directed edges in a tree.

    For each directed edge (src, dst) in the tree, computes the aggregated value
    of all nodes reachable from dst without going back through src. Uses a two-pass
    algorithm: first a reverse DFS to compute child-to-parent aggregations, then
    a forward BFS to compute parent-to-child aggregations.

    Args:
        tree: A networkx Graph representing a tree structure.
        get: Function that extracts a value of type V from each node.
        combine: Binary operation that combines two values of type V.

    Returns:
        Dictionary mapping each directed edge to its aggregated value, representing
        all nodes on the dst side of that edge.
    """
    values: dict[Edge, V] = {}
    root: Node = list(tree.nodes())[0]  # any node will do
    for src, dst in reversed(list(dfs_edges(tree, source=root))):
        acc: V = get(dst)
        for neighbor in tree.neighbors(dst):
            if neighbor != src:
                acc = combine(acc, values[(dst, neighbor)])
        values[(src, dst)] = acc
    for src, dst in edge_bfs(tree, source=root):
        acc: V = get(src)
        for neighbor in tree.neighbors(src):
            if neighbor != dst:
                acc = combine(acc, values[(src, neighbor)])
        values[(dst, src)] = acc
    return values


def compute_or(tree: Graph, get: Callable[[Node], bool]) -> dict[Edge, bool]:
    """Compute boolean OR aggregation over tree edges.

    For each directed edge, computes whether any node on the dst side of that edge
    satisfies the given predicate.

    Args:
        tree: A networkx Graph representing a tree structure.
        get: Predicate function that returns True or False for each node.

    Returns:
        Dictionary mapping each directed edge to a boolean indicating whether any
        node on the dst side satisfies the predicate.
    """
    return aggregate(tree, get, lambda a, b: a or b)


def compute_sum(tree: Graph, get: Callable[[Node], float]) -> dict[Edge, float]:
    """Compute sum aggregation over tree edges.

    For each directed edge, computes the sum of values from all nodes on the dst
    side of that edge.

    Args:
        tree: A networkx Graph representing a tree structure.
        get: Function that returns a numeric value for each node.

    Returns:
        Dictionary mapping each directed edge to the sum of all node values on
        the dst side of that edge.
    """
    return aggregate(tree, get, lambda a, b: a + b)


def closure(tree: Graph, e: Edge) -> set[Node]:
    """Find all nodes on the inside of a directed edge in a tree.

    Given a directed edge (outside, inside), returns the set of all nodes reachable
    from 'inside' without crossing back through 'outside'. This represents one of
    the two connected components that would result from cutting this edge.

    Args:
        tree: A networkx Graph representing a tree structure.
        e: A directed edge (outside, inside) in the tree.

    Returns:
        Set of nodes on the 'inside' side of the edge, excluding the 'outside' node.
    """
    outside, inside = e
    nodes: set[Node] = {inside, outside}
    wl: list[Node] = [inside]
    while wl:
        current: Node = wl.pop()
        for neighbor in tree.neighbors(current):
            if neighbor not in nodes:
                wl.append(neighbor)
                nodes.add(neighbor)
    nodes.remove(outside)
    return nodes


def cut_edges_between(graph: Graph, src: set[Node], dst: set[Node]) -> Iterator[Edge]:
    """Generate all edges crossing from src to dst in a graph.

    Yields directed edges (x, y) where x is in src and y is a neighbor in dst.

    Args:
        graph: A networkx Graph.
        src: Set of source nodes.
        dst: Set of destination nodes.

    Yields:
        Directed edges from src nodes to dst nodes.
    """
    for x in src:
        for y in graph.neighbors(x):
            if y in dst:
                yield (x, y)


def border_nodes(
    graph: Graph, src: set[Node], dst: set[Node]
) -> tuple[set[Node], set[Node]]:
    """Find nodes on the boundary between two node sets.

    Identifies which nodes in src and dst are adjacent to nodes in the other set.

    Args:
        graph: A networkx Graph.
        src: Set of source nodes.
        dst: Set of destination nodes.

    Returns:
        A tuple (src_border, dst_border) where src_border contains nodes in src
        that have neighbors in dst, and dst_border contains nodes in dst that
        have neighbors in src.
    """
    src_nodes: set[Node] = set()
    dst_nodes: set[Node] = set()
    for x, y in cut_edges_between(graph, src, dst):
        src_nodes.add(x)
        dst_nodes.add(y)
    return src_nodes, dst_nodes
