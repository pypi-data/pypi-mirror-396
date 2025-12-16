# HIF for NetworkX

This package implements functions for the Hypergraph data structure in the [HIF](https://github.com/pszufe/HIF-standard) standard for higher-order network data. It builds hypergraphs based on a decomposition into three NetworkX graphs, `H = (V,E,I)` where:
* `V = {v}` is a finite, non empty set of vertices or nodes,
* `E = {e}` is a finite, non-empty set of edges or hyperedges, and
* `I ⊆ VxE` is a set of incidences, that is, pairs `(v,e)` of nodes and edges.

The implementation details can be found in [src/nx_hif/hif.py](src/nx_hif/hif.py).
