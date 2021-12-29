from collections import defaultdict, deque

from tqdm import tqdm

import config


class Graph(object):
    """Graph data structure, undirected by default."""

    def __init__(self, connections, directed=False):
        self._graph = defaultdict(set)
        self._directed = directed
        self.add_connections(connections)

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self._graph))

    def add(self, node1, node2, cost=1):
        """Add connection between node1 and node2"""

        self._graph[node1].add(node2)
        if not self._directed:
            self._graph[node2].add(node1)

    def add_connections(self, connections):
        """Add connections (list of tuple pairs) to graph"""

        for node1, node2 in connections:
            self.add(node1, node2)

    def find_all_paths(self, start, end, path=[]):
        """Find all path between node1 and node2 recursively, very slow though"""
        path = path + [start]
        if start == end:
            return [path]
        if not start in self._graph.keys():
            return []
        paths = []
        for node in self._graph[start]:
            if node not in path:
                newpaths = self.find_all_paths(node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
                    if len(paths) >= config.ROUTES_FOUND_END:
                        return paths
        return paths

    def find_path(self, node1, node2, path=[]):
        """Delegates to the best version"""
        path_iter = self.find_path_iterative(node1, node2, path=[])
        return path_iter

    def find_path_iterative(self, node1, node2, path=[]):
        """Find any path between node1 and node2 iteratively (may not be shortest)"""

        stack = []
        stack.append((node1, node2))
        cur_path = []

        with tqdm(total=len(self._graph.keys()) * len(self._graph.values())) as pbar:
            while stack:
                args = stack.pop()
                (node1, node2) = args
                cur_path += [node1]

                if node1 == node2:
                    return cur_path
                if node1 not in self._graph:
                    break
                for node in self._graph[node1]:
                    if node not in cur_path:
                        args = (node, node2)
                        stack.append(args)
                    pbar.update(1)
        return None

    def find_path_recursive(self, node1, node2, path=[]):
        """Find any path between node1 and node2 recursively (may not be shortest)"""

        path = path + [node1]
        if node1 == node2:
            return path
        if node1 not in self._graph:
            return None
        for node in self._graph[node1]:
            if node not in path:
                new_path = self.find_path_recursive(node, node2, path)
                if new_path:
                    return new_path
        return None

    def find_shortest_path(self, start, end):
        """Finds shortest path efficiently"""
        #  From https://www.python.org/doc/essays/graphs/

        dist = {start: [start]}
        q = deque([start])
        while len(q):
            at = q.popleft()
            for next in self._graph[at]:
                if next not in dist:
                    # Optimal solution would be:
                    # dist[next] = [dist[at], next]
                    dist[next] = dist[at] + [next]
                    q.append(next)
        return dist.get(end)

    def is_connected(self, node1, node2):
        """Is node1 directly connected to node2"""

        return node1 in self._graph and node2 in self._graph[node1]

    def remove(self, node):
        """Remove all references to node"""

        for n, cxns in self._graph.items():
            try:
                cxns.remove(node)
            except KeyError:
                pass
        try:
            del self._graph[node]
        except KeyError:
            pass
