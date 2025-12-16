import gzip
import networkx as nx
import json
from .hif import *


def write_hif(G: HyperGraph, path):
    data = encode_hif_data(G)
    with open(path, "w") as file:
        json.dump(data, file, indent=2)

def encode_hif_data(G: HyperGraph):
    V, E, I = G
    incidences = []
    edges = []
    nodes = []
    for u, v, k, a in hif_incidences(G, data=True):
        a = a.copy()
        if u[1] == V.graph["incidence_pair_index"]:
            u, v = v[0], u[0]
        else:
            u, v = u[0], v[0]
        direction = a.pop("direction", "head")
        # TODO multi-incidence is not part of the HIF standard
        incidence = {"edge": u, "node": v, "attrs": {"key": k, **a}}
        # TODO mandatory for directed
        if direction != "head":
            incidence["direction"] = direction
        incidences.append(incidence)
    for u, d in hif_nodes(G, data=True):
        a = d.copy()
        u_in_I = (u, V.graph["incidence_pair_index"])
        if len(a) > 0 or u_in_I not in I:
            node = {"node": u, "attrs": a}
            nodes.append(node)
    for u, d in hif_edges(G, data=True):
        a = d.copy()
        u_in_I = (u, E.graph["incidence_pair_index"])
        if len(a) > 0 or u_in_I not in I:
            edge = {"edge": u, "attrs": a}
            edges.append(edge)
    # TODO network-type
    return {"incidences": incidences, "edges": edges, "nodes": nodes}

def add_incidence(G: HyperGraph, incidence):
    attrs = incidence.get("attrs", {})
    edge_id = incidence["edge"]
    node_id = incidence["node"]
    direction = incidence.get("direction", "head")
    # TODO multi-incidence is not part of the HIF standard
    key = attrs.pop("key", 0)
    if "weight" in incidence:
        attrs["weight"] = incidence["weight"]
    hif_add_incidence(G, edge_id, node_id, direction, key, **attrs)

def add_edge(G: HyperGraph, edge):
    attrs = edge.get("attrs", {})
    edge_id = edge["edge"]
    if "weight" in edge:
        attrs["weight"] = edge["weight"]
    hif_add_edge(G, edge_id, **attrs)

def add_node(G: HyperGraph, node):
    attrs = node.get("attrs", {})
    node_id = node["node"]
    if "weight" in node:
        attrs["weight"] = node["weight"]
    hif_add_node(G, node_id, **attrs)

def read_hif(path):
    with open(path) as file:
        data = json.load(file)
    return read_hif_data(data)

def read_hif_gzip(path):
    with gzip.open(path, "r") as fin:
        data = json.load(fin)
    return read_hif_data(data)

def read_hif_data(data):
    G_attrs = data.get("metadata", {})
    if "network-type" in data:
        G_attrs["network-type"] = data["network-type"]
    G = hif_create(**G_attrs)
    for i in data["incidences"]:
        add_incidence(G, i)
    for e in data.get("edges", []):
        add_edge(G, e)
    for n in data.get("nodes", []):
        add_node(G, n)
    # note that this is the standard technique for disjoint unions.
    # it means ids are not preserved and we need to save edge and node ids in attributes.
    # G = nx.convert_node_labels_to_integers(G)
    return G
