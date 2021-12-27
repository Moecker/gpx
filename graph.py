import logging
from collections import defaultdict, deque
from tqdm import tqdm
import itertools


class Graph:
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.costs has all the costs between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.costs = {}

    def nodes(self):
        return list(itertools.chain.from_iterable(self.edges.values()))

    def keys(self):
        return self.edges.keys()

    def add(self, from_node, to_node, cost):
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.costs[(from_node, to_node)] = cost
        self.costs[(to_node, from_node)] = cost

    def find_shortest_path(self, start, end):
        """From https://www.python.org/doc/essays/graphs/"""
        dist = {start: [start]}
        q = deque([start])
        while len(q):
            at = q.popleft()
            for next in self.edges[at]:
                if next not in dist:
                    # Optimal solution would be:
                    # dist[next] = [dist[at], next]
                    dist[next] = dist[at] + [next]
                    q.append(next)
        return dist.get(end)

    def dijkstra(self, initial, end):
        """From https://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php"""
        # Shortest paths is a dict of nodes whose value is a tuple of (previous node, cost)
        shortest_paths = {initial: (None, 0)}
        current_node = initial
        visited = set()

        with tqdm(total=len(self.edges)) as pbar:
            while current_node != end:
                visited.add(current_node)
                destinations = self.edges[current_node]
                cost_to_current_node = shortest_paths[current_node][1]

                for next_node in destinations:
                    cost = self.costs[(current_node, next_node)] + cost_to_current_node
                    if next_node not in shortest_paths:
                        shortest_paths[next_node] = (current_node, cost)
                    else:
                        current_shortest_cost = shortest_paths[next_node][1]
                        if current_shortest_cost > cost:
                            shortest_paths[next_node] = (current_node, cost)

                next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
                if not next_destinations:
                    pbar.n = len(self.edges)
                    return None
                # The next node is the destination with the lowest cost
                current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
                pbar.update(1)

            pbar.n = len(self.edges)
            pbar.refresh()

        # Work back through destinations in shortest path
        path = []
        while current_node is not None:
            path.append(current_node)
            next_node = shortest_paths[current_node][0]
            current_node = next_node

        # Reverse path
        path = path[::-1]
        logging.info(f"Dijksra found a path of length {len(path)}.")
        return path

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self.edges))
