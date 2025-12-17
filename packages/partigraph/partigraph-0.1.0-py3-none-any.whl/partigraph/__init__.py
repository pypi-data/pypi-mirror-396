"""Partigraph: Graph partitioning algorithms using random spanning trees.

This package implements algorithms for partitioning graphs into districts of
approximately equal weight using random spanning trees and iterative improvement.
"""

from partigraph.ust import random_spanning_tree
from partigraph.spanning_tree import (
    Node,
    Edge,
    aggregate,
    compute_or,
    compute_sum,
    closure,
    cut_edges_between,
    border_nodes,
)
from partigraph.partition import (
    Partitioner,
    search_for_partition,
    SetWeight,
    Division,
)

__version__ = "0.1.0"

__all__ = [
    # Core algorithm
    "Partitioner",
    "search_for_partition",
    # Spanning tree generation
    "random_spanning_tree",
    # Spanning tree utilities
    "aggregate",
    "compute_or",
    "compute_sum",
    "closure",
    "cut_edges_between",
    "border_nodes",
    # Type aliases
    "Node",
    "Edge",
    "SetWeight",
    "Division",
]
