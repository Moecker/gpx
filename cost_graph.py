import logging
import math
import graph
from collections import defaultdict
from functools import partial
import pprint


class CostGraph(graph.Graph):
    def __init__(self, _):
        self._graph = defaultdict(partial(defaultdict, int))

    def add(self, node1, node2, cost=1):
        self._graph[node1].update({node2: cost})
        self._graph[node2].update({node1: cost})

    def dijkstra(self, start, end):
        graph = self._graph
        D = {}  # Final distances dict
        P = {}  # Predecessor dict
        max_weight = 0

        for node in graph.keys():
            D[node] = 0  # Vertices are unreachable
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
        logging.info(f"Dijksra found a path with weight {max_weight}")
        logging.info(f"Graph {pprint.pformat(D)}")
        return path

    def dijkstra_cost(self, start, end):
        D = {}  # Final distances dict
        P = {}  # Predecessor dict
        minimum_costs = math.inf

        for node in self._graph.keys():
            D[node] = -1  # Vertices are unreachable
            P[node] = None

        D[start] = math.inf  # The start vertex needs no move

        unseen_nodes = list(self._graph.keys())

        while len(unseen_nodes) > 0:
            longest = None
            node = None
            for temp_node in unseen_nodes:
                if longest == None:
                    longest = D[temp_node]
                    node = temp_node
                elif D[temp_node] > longest:
                    longest = D[temp_node]
                    node = temp_node

            unseen_nodes.remove(node)

            for child_node, child_value in self._graph[node].items():
                current_costs = D[node] + child_value

                if D[child_node] < current_costs:
                    minimum_costs = current_costs
                    D[child_node] = current_costs
                    P[child_node] = node

        path = []
        node = end

        while not (node == start):
            if path.count(node) == 0:
                path.insert(0, node)
                node = P[node]
            else:
                break

        path.insert(0, start)
        logging.info(f"Dijksra found a path with costs {minimum_costs}")
        logging.info(f"Graph {pprint.pformat(D)}")
        return path

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self._graph))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, dict(self._graph))

    def dijkstra_original(self, start, end):
        D = {}
        P = {}

        for node in self._graph.keys():
            D[node] = -1
            P[node] = ""

        D[start] = 0
        unseen_nodes = list(self._graph.keys())

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
            for child_node, child_value in self._graph[node].items():
                if D[child_node] < D[node] + child_value:
                    D[child_node] = D[node] + child_value
                    P[child_node] = node
        path = []
        node = end

        while not (node == start):
            if path.count(node) == 0:
                path.insert(0, node)
                node = P[node]
            else:
                break

        path.insert(0, start)
        return path
