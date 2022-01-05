import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.shortest_paths import weighted
import astar
import os
import pickle

import gpx_tools


def node_label(orig):
    return str(orig.source) if orig.source else f"{orig.latitude:.2f},{orig.longitude:.2f}"


gpx_tools.SimplePoint.__repr__ = node_label

path = "tmp/maps/100_py_default_bikeline_fi_1_100_map.p"
path = "test/tmp/maps/1_py_smart_test_gpx_long_1_1_map.p"
path = "test/tmp/maps/1_py_smart_test_gpx_test_munich_augsburg_intersection_1_1_map.p"
path = "test/tmp/maps/1_py_smart_test_gpx_example_1_1_map.p"
path = "test/tmp/maps/1_py_smart_test_gpx_example_10_1_map.p"
path = "test/tmp/maps/1_py_smart_test_gpx_test_munich_dachau_detour_100_1_map.p"

with open(path, "rb") as f:
    g = pickle.load(f)

G = nx.Graph((k, v, {"weight": weight}) for k, vs in g.friends.items() for v, weight in vs.items())
print(G)

pos = nx.spring_layout(G)
nx.draw_networkx(G, pos, with_labels=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "weight"))

print(list(g.friends.keys()))

# key1 = list(g.friends.keys())[4]
# key2 = list(g.friends.keys())[13]
# print(key1)
# print(key2)

# print(G.edges(key1))
# print(G.edges(key2))

# print(nx.astar_path(G, key1, key2))

plt.show()
