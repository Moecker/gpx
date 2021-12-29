import queue
from collections import defaultdict, deque

from tqdm import tqdm


class Graph:
    def __init__(self):
        self.friends = defaultdict(list)

    def init_with_friends(self, friends):
        self.friends = friends

    def add(self, n1, n2, cost):
        self.friends[n1].append((n2, cost))
        self.friends[n2].append((n1, cost))

    # Not used, not tested
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

    # Not used, not tested
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
