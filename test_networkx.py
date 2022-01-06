import pickle

import matplotlib.pyplot as plt
import networkx as nx
import networkx_adapter

import build_graph
import facade
import gpx_tools

networkx_adapter.patch()

DRAW = True

gpx_tools.SimplePoint.__repr__ = (
    lambda orig: str(orig.source) if orig.source else f"{orig.latitude:.2f},{orig.longitude:.2f}"
)
nx.Graph.keys = lambda g: g.nodes()

path = "test/tmp/maps/1_py_smart_test_gpx_example_1_1_map.p"

with open(path, "rb") as f:
    g = pickle.load(f)

G = nx.Graph((k, v, {"weight": weight}) for k, vs in g.friends.items() for v, weight in vs.items())
print(G)

cities = facade.load_worldcities()
start_gps, end_gps = facade.find_start_and_end(cities, "Erfurt", "Leipzig")
first, last = build_graph.get_closest_start_and_end(G, start_gps, end_gps)

for node, neighbors in G.adj.items():
    key, _ = gpx_tools.deannotate(node)
    for other_node, cost in neighbors.items():
        other_key, _ = gpx_tools.deannotate(other_node)

print(nx.astar_path(G, first, last))

if DRAW:
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "weight"))
    plt.show()
