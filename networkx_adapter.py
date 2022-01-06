import networkx as nx
import distance
import config


def nx_adjust_weight(g, n1, n2, cost):
    g.adj[n1][n2]["weight"] = cost
    g.adj[n2][n1]["weight"] = cost


def nx_build_heuristic(p1, p2):
    return distance.haversine_gpx(p1, p2) * config.HEURISTIC_SCALE_FACTOR


def nx_cost(g, p1, p2):
    path = nx.astar_path(g, p1, p2, nx_build_heuristic)
    weight_fn = lambda u, v, data: data.get("weight", 1)
    cost = sum(weight_fn(u, v, g[u][v]) for u, v in zip(path[:-1], path[1:]))
    return path, cost


def patch():
    # Monkey Patches to avoid creating a own class.
    # Consider using a real class.
    nx.Graph.keys = lambda g: g.nodes()
    nx.Graph.weights = lambda g: [0, 0]
    nx.Graph.build_heuristic = lambda p1, p2: None
    nx.Graph.dijkstra = nx_cost
    nx.Graph.adjust_weight = nx_adjust_weight
    nx.Graph.friends = nx.Graph.adj
