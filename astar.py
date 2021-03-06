from collections import defaultdict, deque
from functools import partial
from tqdm import tqdm
import config
import distance
import itertools
import logging
import math

# Originally, this was a graph which implemented a tuple instead of a dict (for neighbor nodes and costs).
# Setting this to True would use this old implementation
USE_TUPLE_IMPL = False


class Graph:
    """
    A Graph in a structure
    if USE_TUPLE_IMPL:
        dict[key=GPSPoint, value=list(tuple(NeighborGPSPoint, Costs))]
    if not USE_TUPLE_IMPL:
        dict[key=GPSPoint, value=dict[key=NeighborGPSPoint, value=Costs)]]
    """

    def __init__(self):
        self.friends = defaultdict(list) if USE_TUPLE_IMPL else defaultdict(partial(defaultdict, int))
        self.heuristic = defaultdict(int)

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self.friends))

    def a_star_algorithm(self, start, stop):
        """From https://www.pythonpool.com/a-star-algorithm-python/"""
        # In this open_lst is a list of nodes which have been visited, but who's
        # neighbors haven't all been always inspected.
        # The closed_lst is a list of nodes which have been visited
        # and who's neighbors have been always inspected
        open_lst = set([start])
        closed_lst = set([])

        # Dict poo has present distances from start to all other nodes
        poo = {}
        poo[start] = 0

        # Dict par contains an adjacent mapping of all nodes
        par = {}
        par[start] = start

        total_pbar = len(self.nodes()) + len(self.keys())
        with tqdm(total=total_pbar, disable=logging.getLogger().level > logging.INFO) as pbar:
            while len(open_lst) > 0:
                n = None

                # It will find a node with the lowest value of f()
                for v in open_lst:
                    if n == None or poo[v] + self.h(v) < poo[n] + self.h(n):
                        n = v
                if n == None:
                    return None, math.inf

                pbar.set_description(f"Searching {str(n).ljust(180):.100s}")

                # If the current node is the end node then we start again from start
                if n == stop:
                    reconst_path = []
                    while par[n] != n:
                        reconst_path.append(n)
                        n = par[n]

                    reconst_path.append(start)
                    reconst_path.reverse()
                    return reconst_path, poo[stop]

                # For all the neighbors of the current node do
                for (m, cost) in self.get_neighbors(n):
                    # If the current node is not present in both open_lst and closed_lst
                    # add it to open_lst and note n as it's par
                    if m not in open_lst and m not in closed_lst:
                        open_lst.add(m)
                        par[m] = n
                        poo[m] = poo[n] + cost
                    # Otherwise, check if it's quicker to first visit n, then m
                    # and if it is, update par data and poo data,
                    # and if the node was in the closed_lst, move it to open_lst
                    else:
                        new_cost = poo[n] + cost
                        if poo[m] > new_cost:
                            poo[m] = new_cost
                            par[m] = n

                            if m in closed_lst:
                                closed_lst.remove(m)
                                open_lst.add(m)

                # Remove n from the open_lst, and add it to closed_lst,
                # because all of his neighbors were inspected
                open_lst.remove(n)
                closed_lst.add(n)
                pbar.update(1)

        return None, math.inf

    def add(self, n1, n2, cost):
        if USE_TUPLE_IMPL:
            self.friends[n1].append((n2, cost))
            self.friends[n2].append((n1, cost))
        else:
            self.friends[n1][n2] = cost
            self.friends[n2][n1] = cost

    def adjust_weight(self, n1, n2, cost):
        if not USE_TUPLE_IMPL:
            self.friends[n1][n2] = cost
            self.friends[n2][n1] = cost

    def build_heuristic(self, end):
        for key in self.keys():
            dis = distance.haversine_gpx(key, end)
            self.heuristic[key] = dis * config.HEURISTIC_SCALE_FACTOR

    def dijkstra(self, start, stop):
        return self.a_star_algorithm(start, stop)

    def find_shortest_path(self, start, end):
        """From https://www.python.org/doc/essays/graphs/"""
        dist = {start: [start]}
        q = deque([start])
        while len(q):
            at = q.popleft()
            for next in self.friends[at]:
                if next not in dist:
                    # Optimal solution would be:
                    # dist[next] = [dist[at], next]
                    dist[next] = dist[at] + [next]
                    q.append(next)
        return dist.get(end), 0

    def get_neighbors(self, v):
        return self.friends[v] if USE_TUPLE_IMPL else [(k, v) for k, v in self.friends[v].items()]

    def h(self, n):
        return self.heuristic[n]

    def init_with_friends(self, friends):
        self.friends = friends

    def keys(self):
        return self.friends.keys()

    def nodes(self):
        return (
            [t[0] for t in list(itertools.chain.from_iterable(self.friends.values()))]
            if USE_TUPLE_IMPL
            else [t for t in list(itertools.chain.from_iterable(self.friends.values()))]
        )

    def weights(self):
        return (
            [t[1][0][1] for t in [t for t in list(self.friends.items())]]
            if USE_TUPLE_IMPL
            else [val for sublist in self.friends.values() for val in sublist.values()]
        )
