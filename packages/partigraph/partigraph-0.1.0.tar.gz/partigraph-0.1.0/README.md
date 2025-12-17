# Partigraph

Graph partitioning algorithms using random spanning trees.

Partigraph implements algorithms for partitioning graphs into districts of approximately equal weight. It uses random spanning trees to find transfer moves between partitions and iteratively improve divisions to meet weight constraints.

## Features

- **Uniform Random Spanning Trees**: Implementation of Wilson's algorithm for generating uniformly random spanning trees
- **Weight-Balanced Partitioning**: Divide graphs into districts with configurable weight constraints
- **Iterative Improvement**: Refine partitions through random spanning tree-based transfers
- **Flexible Weight Functions**: Support for custom node weight functions or node attributes

## Installation

```bash
pip install partigraph
```



## Algorithm

Partigraph uses a divide-and-conquer approach:

1. Generate a random spanning tree of the graph using Wilson's algorithm
2. Find the edge cut that best divides the graph into the target weights
3. Recursively partition each side
4. Iteratively improve the partition by finding beneficial transfers between districts

The random spanning tree approach ensures good connectivity properties and helps avoid gerrymandering-like artifacts.

## Requirements

- Python >= 3.12
- NetworkX

## License

MIT License - see LICENSE file for details

## References

Wilson's algorithm for uniform random spanning trees:
- Wilson, D. B. (1996). "Generating Random Spanning Trees More Quickly than the Cover Time"