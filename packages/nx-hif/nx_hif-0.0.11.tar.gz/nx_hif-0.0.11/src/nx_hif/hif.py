from itertools import chain
import networkx as nx


type HyperGraph = tuple[nx.MultiDiGraph, nx.MultiDiGraph, nx.MultiGraph]
"""
A hypergraph is a system H = (V,E,I) where
V = {v} is a finite, non empty set of vertices or nodes,
E = {e} is a finite, non-empty set of edges or hyperedges, and
I ⊆ VxE is a set of incidences, that is, pairs (v,e) of nodes and edges.
"""


def hif_create(**I_attrs) -> HyperGraph:
    V = nx.MultiDiGraph(incidence_pair_index=0)
    E = nx.MultiDiGraph(incidence_pair_index=1)
    I = nx.MultiGraph(**I_attrs)
    return V, E, I

def hif_new_edge(G: HyperGraph, **attr):
    _, E, _ = G
    edge = E.number_of_nodes()
    hif_add_edge(G, edge, **attr)
    return edge

def hif_new_node(G: HyperGraph, **attr):
    V, _, _ = G
    node = V.number_of_nodes()
    hif_add_node(G, node, **attr)
    return node

def hif_node(G: HyperGraph, node):
    V, _, _ = G
    return V.nodes[node]

def hif_edge(G: HyperGraph, edge):
    _, E, _ = G
    return E.nodes[edge]

def hif_incidence(G: HyperGraph, edge, node, key=0):
    # TODO encapsulate tupling with incidence_pair_index
    V, E, I = G
    return I.edges[
        (edge, E.graph["incidence_pair_index"]),
        (node, V.graph["incidence_pair_index"]),
        key]

def hif_nodes(G: HyperGraph, data=False):
    V, _, _ = G
    return V.nodes(data=data)

def hif_number_of_all(G: HyperGraph):
    V, E, _ = G
    return V.number_of_nodes() + E.number_of_nodes()

def hif_edges(G: HyperGraph, data=False):
    _, E, _ = G
    return E.nodes(data=data)

def hif_edge_nodes(G: HyperGraph, edge, direction="head"):
    """
    An edge e ∈ E can be mapped to the collection of vertices with which it has an
    incidence: e → {v ∈ V : (v,e) ∈ I}
    """
    _, E, I = G
    ekey = (edge, E.graph["incidence_pair_index"])
    return (n[0] if e == ekey else e[0]
            for e, n, d in I.edges(ekey, data=True)
            if d["direction"] == direction)

def hif_node_edges(G: HyperGraph, node, direction="head"):
    V, _, I = G
    nkey = (node, V.graph["incidence_pair_index"])
    return (e[0] if n == nkey else n[0]
            for e, n, d in I.edges(nkey, data=True)
            if d["direction"] == direction)

def hif_node_incidences(G: HyperGraph, node, direction="head", key=0, **attr):
    V, _, I = G
    n = (node, V.graph["incidence_pair_index"])
    for (ee0, ee1, k, d) in I.edges(n, data=True, keys=True):
        if key != k or d["direction"] != direction:
            continue
        if ee0[1] == V.graph["incidence_pair_index"]:
            e, n = ee1[0], ee0[0]
        else:
            e, n = ee0[0], ee1[0]
        yield e, n, k, d

def hif_edge_incidences(G: HyperGraph, edge, direction="head", key=0):
    _, E, I = G
    e = (edge, E.graph["incidence_pair_index"])
    for (ee0, ee1, k, d) in I.edges(e, data=True, keys=True):
        if key != k or d["direction"] != direction:
            continue
        if ee0[1] == E.graph["incidence_pair_index"]:
            e, n = ee0[0], ee1[0]
        else:
            e, n = ee1[0], ee0[0]
        yield e, n, k, d

def hif_incidences(G: HyperGraph, edge=None, node=None, direction="head", key=0, data=False):
    V, E, I = G
    edges = []
    nodes = []
    if edge is not None:
        edges = [(edge, E.graph["incidence_pair_index"])]
    else:
        edges = ((e, E.graph["incidence_pair_index"]) for e in E)

    if node is not None:
        nodes = [(node, V.graph["incidence_pair_index"])]
    else:
        nodes = ((n, V.graph["incidence_pair_index"]) for n in V)

    return I.edges(chain(edges, nodes), data=data, keys=True)

def hif_add_edge(G: HyperGraph, edge, **attr):
    """Adds an edge with a specific ID. See also: hif_new_edge."""
    _, E, I = G
    E.add_node(edge, **attr)
    I.add_node((edge, E.graph["incidence_pair_index"]))

def hif_add_node(G: HyperGraph, node, **attr):
    """Adds a node with a specific ID. See also: hif_new_node."""
    V, _, I = G
    V.add_node(node, **attr)
    I.add_node((node, V.graph["incidence_pair_index"]))

def hif_add_incidence(G: HyperGraph, edge, node, direction="head", key=0, **attr):
    V, E, I = G
    I.add_edge(
        (edge, E.graph["incidence_pair_index"]),
        (node, V.graph["incidence_pair_index"]),
        key=key, direction=direction, **attr)
    E.add_node(edge)
    V.add_node(node)

def hif_dualize(G: HyperGraph):
    V, E, _ = G
    V.graph["incidence_pair_index"], E.graph["incidence_pair_index"] = \
        E.graph["incidence_pair_index"], V.graph["incidence_pair_index"]

def hif_s_closeness_centrality(G: HyperGraph, s: int):
    """
    See "Hypernetwork science via high-order hypergraph walks":
    https://doi.org/10.1140/epjds/s13688-020-00231-0
    """
    # TODO generalize s
    assert s == 1
    _, E, I = G
    spl = tuple((u, v) for (u, t), v in nx.shortest_path_length(I) if t == E.graph["incidence_pair_index"])
    scc = {u: ((len(spl) - 1) / sum(b/2 for (a, t), b in v.items() if t == E.graph["incidence_pair_index"])) for u, v in spl}
    return scc
