import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.shortest_paths import weighted
import astar
import os
import pickle

# G = nx.Graph()

# G.add_node(1)
# G.add_node(2)
# G.add_node(3)

# G.add_edge(1, 2, weight=1)
# G.add_edge(1, 3, weight=10)
# G.add_edge(2, 3, weight=1)

# p = nx.astar_path(G, 1, 3)

# nx.draw(G, with_labels=True, font_weight="bold")

# pos = nx.spring_layout(G)
# nx.draw_networkx(G, pos)
# labels = nx.get_edge_attributes(G, "weight")
# nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

# G2 = nx.Graph(g.friends)

# pos = nx.spring_layout(G2)
# nx.draw_networkx(G2, pos)
# labels = nx.get_edge_attributes(G2, "cost")
# nx.draw_networkx_edge_labels(G2, pos, edge_labels=labels)

# plt.show()

with open("tmp/maps/100_py_default_bikeline_ch_1_100_map.p", "rb") as f:
    g = pickle.load(f)

G = nx.Graph((k, v, {'weight': weight}) for k, vs in g.friends.items() for v, weight in vs.items())
print(G)
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos)
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "weight"))
nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, "weight"))
plt.show()
