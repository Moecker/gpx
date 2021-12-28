import itertools
from collections import defaultdict, deque
import queue
import distance
import config

from tqdm import tqdm


class Graph:
    def __init__(self):
        self.friends = defaultdict(list)
        self.heuristic = defaultdict(int)

    def nodes(self):
        return [t[0] for t in list(itertools.chain.from_iterable(self.friends.values()))]

    def keys(self):
        return self.friends.keys()

    def init_with_friends(self, friends):
        self.friends = friends

    def add(self, n1, n2, cost):
        self.friends[n1].append((n2, cost))
        self.friends[n2].append((n1, cost))

    def get_neighbors(self, v):
        return self.friends[v]

    def h(self, n):
        return self.heuristic[n]

    def weights(self):
        all_nodes = [t for t in list(self.friends.items())]
        all_weights = [t[1][0][1] for t in all_nodes]
        return all_weights

    def build_heuristic(self, end):
        for key in self.keys():
            dis = distance.haversine_gpx(key, end)
            self.heuristic[key] = dis * config.HEURISTIC_SCALE_FACTOR

    def dijkstra(self, start, stop):
        return self.a_star_algorithm(start, stop)

    def a_star_algorithm(self, start, stop):
        """From https://www.pythonpool.com/a-star-algorithm-python/"""
        # In this open_lst is a list of nodes which have been visited, but who's
        # neighbors haven't all been always inspected.
        # The closed_lst is a list of nodes which have been visited
        # and who's neighbors have been always inspected
        open_lst = set([start])
        closed_lst = set([])

        # Dict poo has present distances from start to all other nodes
        # The default value is +infinity
        poo = {}
        poo[start] = 0

        # Dict par contains an adjacent mapping of all nodes
        par = {}
        par[start] = start

        total_pbar = len(self.keys())
        with tqdm(total=total_pbar) as pbar:
            while len(open_lst) > 0:
                n = None

                # It will find a node with the lowest value of f()
                for v in open_lst:
                    if n == None or poo[v] + self.h(v) < poo[n] + self.h(n):
                        n = v

                if n == None:
                    pbar.n = total_pbar
                    return None

                # If the current node is the end node then we start again from start
                if n == stop:
                    reconst_path = []

                    while par[n] != n:
                        reconst_path.append(n)
                        n = par[n]

                    reconst_path.append(start)
                    reconst_path.reverse()

                    pbar.n = total_pbar
                    return reconst_path

                # For all the neighbors of the current node do
                for (m, weight) in self.get_neighbors(n):
                    # If the current node is not present in both open_lst and closed_lst
                    # add it to open_lst and note n as it's par
                    if m not in open_lst and m not in closed_lst:
                        open_lst.add(m)
                        par[m] = n
                        poo[m] = poo[n] + weight

                    # Otherwise, check if it's quicker to first visit n, then m
                    # and if it is, update par data and poo data,
                    # and if the node was in the closed_lst, move it to open_lst
                    else:
                        if poo[m] > poo[n] + weight:
                            poo[m] = poo[n] + weight
                            par[m] = n

                            if m in closed_lst:
                                closed_lst.remove(m)
                                open_lst.add(m)

                # Remove n from the open_lst, and add it to closed_lst,
                # because all of his neighbors were inspected
                open_lst.remove(n)
                closed_lst.add(n)
                pbar.update(1)
                
        pbar.n = total_pbar
        return None

    def find_shortest_path(self, start, end):
        """From https://www.python.org/doc/essays/graphs/"""
        dist = {start: [start]}
        q = deque([start])
        while len(q):
            at = q.popleft()
            for next in self.friends[at]:
                next = next[0]  # For the tuple thingy
                if next not in dist:
                    # Optimal solution would be:
                    # dist[next] = [dist[at], next]
                    dist[next] = dist[at] + [next]
                    q.append(next)
        return dist.get(end)

    # TODO Not used, not tested
    def find_shortest_path_prio_queue(self, start, end):
        """From https://stackoverflow.com/questions/48313993/uniform-cost-search-algorithm-with-python"""
        visited = set()  # set of visited nodes
        q = queue.PriorityQueue()  # we store vertices in the (priority) queue as tuples
        # (f, n, path), with
        # f: the cumulative cost,
        # n: the current node,
        # path: the path that led to the expansion of the current node
        q.put((0, start, [start]))  # add the starting node, this has zero *cumulative* cost
        # and it's path contains only itself.
        while not q.empty():  # while the queue is nonempty
            f, current_node, path = q.get()
            visited.add(current_node)  # mark node visited on expansion,
            # only now we know we are on the cheapest path to
            # the current node.

            if current_node == end:  # if the current node is a goal
                return path  # return its path
            else:
                for edge in self.friends[current_node]:
                    child = edge[0]
                    if child not in visited:
                        q.put((f + edge[1], child, path + [child]))

    # TODO Not used, not tested
    def ucs(self, start, end):
        """From https://stackoverflow.com/questions/43354715/uniform-cost-search-in-python"""
        v = start

        visited = set()  # set of visited nodes
        visited.add(v)  # mark the starting vertex as visited
        q = queue.PriorityQueue()  # we store vertices in the (priority) queue as tuples with cumulative cost
        q.put((0, v))  # add the starting node, this has zero *cumulative* cost
        goal_node = None  # this will be set as the goal node if one is found
        parents = {v: None}  # this dictionary contains the parent of each node, necessary for path construction

        while not q.empty():  # while the queue is nonempty
            dequeued_item = q.get()
            current_node = dequeued_item[1]  # get node at top of queue
            current_node_priority = dequeued_item[0]  # get the cumulative priority for later

            if current_node.is_goal:  # if the current node is the goal
                path_to_goal = [current_node]  # the path to the goal ends with the current node (obviously)
                prev_node = (
                    current_node  # set the previous node to be the current node (this will changed with each iteration)
                )

                while prev_node != v:  # go back up the path using parents, and add to path
                    parent = parents[prev_node]
                    path_to_goal.append(parent)
                    prev_node = parent

                path_to_goal.reverse()  # reverse the path
                return path_to_goal  # return it

            else:
                for edge in current_node.out_edges:  # otherwise, for each adjacent node
                    child = edge.to()  # (avoid calling .to() in future)

                    if child not in visited:  # if it is not visited
                        visited.add(child)  # mark it as visited
                        parents[child] = current_node  # set the current node as the parent of child
                        q.put((current_node_priority + edge.weight, child))  # and enqueue it with *cumulative* priority

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, dict(self.friends))
