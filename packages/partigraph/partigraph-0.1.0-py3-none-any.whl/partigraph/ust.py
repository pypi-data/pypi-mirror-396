"""Wilson's algorithm for generating uniform random spanning trees.

This module implements Wilson's algorithm for generating random spanning trees
from a graph with uniform probability distribution over all possible spanning trees.

Reference:
    Generating Random Spanning Trees More Quickly than the Cover Time
    David Bruce Wilson
    https://www.cs.cmu.edu/~15859n/RelatedWork/RandomTrees-Wilson.pdf
"""

import random
from typing import Hashable

from networkx import Graph


def random_spanning_tree(graph: Graph) -> Graph:
    """Generate a uniform random spanning tree from a graph using Wilson's algorithm.

    Wilson's algorithm generates a spanning tree by performing loop-erased random
    walks from each node until reaching the growing tree. This produces a uniformly
    random spanning tree from the set of all possible spanning trees of the graph.

    This implementation assumes the input graph is connected, and will silently
    produce a spanning tree for one connected component if not.

    Args:
        graph: A networkx Graph from which to generate a spanning tree.

    Returns:
        A networkx Graph representing a random spanning tree of the input graph.
        The tree contains all nodes from the input graph and a subset of edges
        that form a tree structure.
    """
    tree: Graph = Graph()
    tree.add_node(random.choice(list(graph.nodes())))

    next: dict[Hashable, Hashable] = {}
    neighbors: dict[Hashable, list[Hashable]] = {
        n: list(graph.neighbors(n)) for n in graph.nodes()
    }
    u: Hashable
    i: Hashable
    for i in graph.nodes():
        u = i
        while u not in tree:
            next[u] = random.choice(neighbors[u])
            u = next[u]
        u = i
        while u not in tree:
            tree.add_node(u)
            u = next[u]

    tree.add_edges_from(next.items())
    return tree
