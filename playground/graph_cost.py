from collections import defaultdict
from functools import partial
import logging
import pprint

import graph_simple


class CostGraph(graph_simple.Graph):
    def __init__(self, _):
        self._graph = defaultdict(partial(defaultdict, int))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, dict(self._graph))

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self._graph))

    def add(self, node1, node2, cost=1):
        self._graph[node1].update({node2: cost})
        self._graph[node2].update({node1: cost})

    def dijkstra(self, start, end):
        graph = self._graph
        D = {}  # Final distances dict
        P = {}  # Predecessor dict
        max_weight = 0

        for node in graph.keys():
            D[node] = -1  # Vertices are unreachable
            P[node] = ""
        D[start] = 0  # The start vertex needs no move
        unseen_nodes = list(graph.keys())  # All nodes are unseen

        while len(unseen_nodes) > 0:
            shortest = None
            node = ""
            for temp_node in unseen_nodes:
                if shortest == None:
                    shortest = D[temp_node]
                    node = temp_node
                elif D[temp_node] < shortest:
                    shortest = D[temp_node]
                    node = temp_node
            unseen_nodes.remove(node)
            for child_node, child_value in graph[node].items():
                weight = D[node] + child_value
                if D[child_node] < D[node] + child_value:
                    D[child_node] = D[node] + child_value
                    P[child_node] = node
                    max_weight = weight
        path = []
        node = end
        while not (node == start):
            if path.count(node) == 0:
                path.insert(0, node)  # Insert the predecessor of the current node
                node = P[node]  # The current node becomes its predecessor
            else:
                break
        path.insert(0, start)  # Finally, insert the start vertex
        logging.info(f"Dijksra found a path of length {path} with weight {max_weight}.")
        logging.info(f"Dijksra path {pprint.pformat(path)}.")
        logging.info(f"Dijksra graph {pprint.pformat(D)}.")
        return path
