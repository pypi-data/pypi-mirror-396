"""Graph partitioning algorithms using random spanning trees.

This module implements algorithms for partitioning graphs into districts of
approximately equal weight. Uses random spanning trees to find transfer moves
between partitions and iteratively improve divisions to meet weight constraints.
"""

from typing import Callable, Iterator

from networkx import Graph

from partigraph.ust import random_spanning_tree
from partigraph.spanning_tree import Node, Edge, compute_or, compute_sum, closure, border_nodes

SetWeight = tuple[set[Node], float]
Division = tuple[SetWeight, SetWeight]


class Partitioner:
    """Partitions graphs into weighted districts using spanning tree cuts.

    Uses a divide-and-conquer approach combined with random spanning trees to
    partition a graph into districts of approximately equal weight. Can iteratively
    improve partitions to satisfy weight constraints.

    Attributes:
        graph: The networkx Graph to partition.
        weight_field: Name of the node attribute to use as weight (if any).
        get_weight: Function that returns the weight of a node.
    """

    graph: Graph
    weight_field: str
    get_weight: Callable[[Node], float]

    def __init__(
        self,
        graph: Graph,
        get_weight: Callable[[Node], float] = lambda x: 1.0,
        weight_field: str = "",
    ) -> None:
        """Initialize a Partitioner for the given graph.

        Args:
            graph: A networkx Graph to partition.
            get_weight: Function to extract weight from a node. Defaults to 1.0 per node.
            weight_field: Name of node attribute to use as weight. If provided, overrides get_weight.
        """
        self.graph = graph
        self.weight_field = weight_field
        if weight_field:
            self.get_weight = lambda x: graph.nodes[x][weight_field]
        else:
            self.get_weight = get_weight

    def compute_weights(self, tree: Graph) -> dict[Edge, float]:
        """Compute weight sums for all directed edges in a tree.

        Args:
            tree: A networkx Graph representing a tree structure.

        Returns:
            Dictionary mapping each directed edge to the sum of weights on the dst side.
        """
        return compute_sum(tree, self.get_weight)

    def random_legal_moves(
        self,
        src: set[Node],
        dst: set[Node],
        keep_adjacent: set[Node] = set(),
    ) -> tuple[Graph, Iterator[tuple[Edge, float]]]:
        """Generate random legal moves from src to dst partition.

        Creates a random spanning tree of src and identifies edges that can be cut
        to transfer nodes to dst. An edge is legal if it reaches the border with dst,
        ensuring transferred nodes connect to dst in the full graph.

        Args:
            src: Source partition (nodes to potentially move from).
            dst: Destination partition (nodes to potentially move to).
            keep_adjacent: If provided, filters out moves that would disconnect src from this set.

        Returns:
            A tuple of (tree, moves) where tree is the random spanning tree of src,
            and moves is an iterator of (edge, weight) pairs for legal cuts.
        """
        border, _ = border_nodes(self.graph, src, dst)
        if not border:
            raise ValueError("Source and destination partitions are not adjacent")
        subgraph: Graph = self.graph.subgraph(src)
        tree: Graph = random_spanning_tree(subgraph)  # type: ignore
        weights: dict[Edge, float] = self.compute_weights(tree)
        reaches: dict[Edge, bool] = compute_or(tree, lambda x: x in border)
        itrtr: filter[tuple[Edge, float]] = filter(
            lambda item: reaches[item[0]], weights.items()
        )
        if keep_adjacent:
            adjacent_border, _ = border_nodes(self.graph, src, keep_adjacent)
            adjacent_counts: dict[Edge, float] = compute_sum(
                tree, lambda x: x in adjacent_border
            )
            itrtr = filter(
                lambda item: adjacent_counts[item[0]] < len(adjacent_border),
                itrtr,
            )
        return tree, itrtr

    def best_move(
        self,
        src: set[Node],
        dst: set[Node],
        target: float,
        keep_adjacent: set[Node] = set(),
    ) -> SetWeight:
        """Find the best move from src to dst to achieve a target weight.

        Selects the legal move whose weight is closest to the target.

        Args:
            src: Source partition.
            dst: Destination partition.
            target: Target weight for the transferred nodes.
            keep_adjacent: If provided, maintains adjacency to this set.

        Returns:
            A tuple (nodes, weight) of the nodes to transfer and their total weight.
            If no legal move exists, returns (empty set, 0.0).
        """
        tree: Graph
        moves: Iterator[tuple[Edge, float]]
        tree, moves = self.random_legal_moves(src, dst, keep_adjacent)
        edge: Edge
        weight: float
        try:
            edge, weight = min(moves, key=lambda item: abs(target - item[1]))
        except ValueError:
            return set(), 0.0
        nodes: set[Node] = closure(tree, edge)
        return nodes, weight

    def improve_division(
        self,
        division: Division,
        target: float,
        keep_adjacents: tuple[set[Node], set[Node]] = (set(), set()),
    ) -> Division:
        """Attempt to improve a division by moving nodes between partitions.

        If one side is too heavy, tries to move nodes to the other side to get
        closer to the target weight. Only makes moves that actually improve the
        division.

        Args:
            division: Current division as ((nodes1, weight1), (nodes2, weight2)).
            target: Target weight for each partition.
            keep_adjacents: Optional tuple of sets to maintain adjacency with.

        Returns:
            Improved division if a beneficial move was found, otherwise the original division.
        """
        (src, src_wt), (dst, dst_wt) = division
        (src_adjacent, dst_adjacent) = keep_adjacents
        nodes: set[Node]
        wt: float
        delta: float = abs(src_wt - target)
        if src_wt > target:
            nodes, wt = self.best_move(src, dst, delta, src_adjacent)
            if 0 < wt < 2 * delta:
                return (src - nodes, src_wt - wt), (dst | nodes, dst_wt + wt)
        else:
            nodes, wt = self.best_move(dst, src, delta, dst_adjacent)
            if 0 < wt < 2 * delta:
                return (src | nodes, src_wt + wt), (dst - nodes, dst_wt - wt)
        return (src, src_wt), (dst, dst_wt)

    def repeatedly_improve_division(
        self,
        target: float,
        limit: int,
        division: Division,
        keep_adjacents: tuple[set[Node], set[Node]] = (set(), set()),
    ) -> Division:
        """Repeatedly improve a division until convergence or limit reached.

        Continues making improvement moves until the target is reached or the
        specified number of consecutive failed attempts is exceeded.

        Args:
            target: Target weight for the first partition.
            limit: Maximum consecutive failed improvement attempts before giving up.
            division: Initial division to improve.
            keep_adjacents: Optional tuple of sets to maintain adjacency with.

        Returns:
            The improved division.
        """
        failed_attempts: int = 0
        while failed_attempts < limit and division[0][1] != target:
            previous: Division = division
            division = self.improve_division(division, target, keep_adjacents)
            if division[0][1] == previous[0][1]:
                failed_attempts += 1
            else:
                failed_attempts = 0
        return division

    def closest_random_division(
        self,
        current: set[Node],
        target: float,
    ) -> Division:
        """Create a random division close to a target weight.

        Generates a random spanning tree of the nodes and selects the edge whose
        cut creates a division closest to the target weight.

        Args:
            current: Set of nodes to divide.
            target: Target weight for one side of the division.

        Returns:
            A division ((nodes1, weight1), (nodes2, weight2)) close to the target.
        """
        subgraph: Graph = self.graph.subgraph(current)
        tree: Graph = random_spanning_tree(subgraph)  # type: ignore
        weights: dict[Edge, float] = self.compute_weights(tree)
        best_edge, best_weight = min(
            weights.items(), key=lambda item: abs(target - item[1])
        )
        d1_nodes: set[Node] = closure(tree, best_edge)
        d1_wt: float = best_weight
        d2_nodes: set[Node] = current - d1_nodes
        d2_wt: float = weights[(best_edge[1], best_edge[0])]
        return (d1_nodes, d1_wt), (d2_nodes, d2_wt)

    def partition_equally[T](
        self,
        all_nodes: set[Node],
        all_weight: float,
        districts: list[T],
        limit: int = 10,
        is_valid: Callable[[float], bool] = lambda wt: True,
        backtrack: int = 1,
    ) -> dict[T, set[Node]]:
        """Recursively partition nodes into equal-weight districts.

        Uses divide-and-conquer: splits nodes in half, recursively partitions each
        half, and returns the combined result. Base case assigns all nodes to a
        single district.

        Args:
            all_nodes: All nodes to partition.
            all_weight: Total weight of all nodes.
            districts: List of district identifiers to assign.
            limit: Maximum improvement attempts per division.
            is_valid: Predicate to check if a weight satisfies constraints.

        Returns:
            Dictionary mapping each district identifier to its set of nodes.

        Raises:
            ValueError: If the partition violates weight constraints.
        """
        if len(districts) == 1:
            if not is_valid(all_weight):
                raise ValueError("Invalid partition: weight constraint violated")
            return {districts[0]: set(all_nodes)}

        mid: int = len(districts) // 2
        d1_districts: list[T] = districts[:mid]
        d2_districts: list[T] = districts[mid:]

        target_per_district: float = all_weight / len(districts)
        scaled_target: float = target_per_district * len(d1_districts)

        for _ in range(backtrack):
            division: Division = self.closest_random_division(all_nodes, scaled_target)
            division = self.repeatedly_improve_division(scaled_target, limit, division)
            (d1_nodes, d1_wt), (d2_nodes, d2_wt) = division

            try:
                p1: dict[T, set[Node]] = self.partition_equally(
                    d1_nodes, d1_wt, d1_districts, limit, is_valid, backtrack
                )
                p2: dict[T, set[Node]] = self.partition_equally(
                    d2_nodes, d2_wt, d2_districts, limit, is_valid, backtrack
                )
                return {**p1, **p2}
            except ValueError:
                continue
        raise ValueError("Failed to find valid partition within backtrack limit")

    def search_for_partition[T](
        self,
        districts: list[T],
        is_valid: Callable[[float], bool],
        limit: int = 10,
        backtrack: int = 1,
    ) -> dict[T, set[Node]]:
        """Search for a valid partition of the graph into districts.

        Repeatedly attempts to partition the graph until a valid partition satisfying
        weight constraints is found.

        Args:
            districts: List of district identifiers.
            is_valid: Predicate to validate partition weights.
            limit: Maximum improvement attempts per division.

        Returns:
            Dictionary mapping district identifiers to node sets.
        """
        nodes: set[Node] = set(self.graph.nodes())
        weight: float = sum(self.get_weight(node) for node in nodes)
        while True:
            try:
                return self.partition_equally(
                    nodes,
                    weight,
                    districts,
                    limit,
                    is_valid,
                    backtrack,
                )
            except ValueError:
                continue


def search_for_partition[T](
    graph: Graph,
    districts: list[T],
    is_valid: Callable[[float], bool],
    limit: int = 10,
    get_pop: Callable[[Node], float] = lambda x: 1.0,
    weight_field: str = "",
    backtrack: int = 3,
) -> dict[T, set[Node]]:
    """Search for a valid partition of a graph into districts.

    Convenience function that creates a Partitioner and searches for a valid partition.

    Args:
        graph: A networkx Graph to partition.
        districts: List of district identifiers.
        is_valid: Predicate to validate partition weights.
        limit: Maximum improvement attempts per division.
        get_pop: Function to extract weight from a node.
        weight_field: Name of node attribute to use as weight.

    Returns:
        Dictionary mapping district identifiers to node sets.
    """
    parter = Partitioner(graph, get_pop, weight_field)
    return parter.search_for_partition(districts, is_valid, limit, backtrack)
