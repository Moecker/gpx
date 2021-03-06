import logging
import math
import unittest

import astar


class TestGraph(unittest.TestCase):
    def test_graph_internet_tuples(self):
        astar.USE_TUPLE_IMPL = True
        friends = {"A": [("B", 1), ("C", 3), ("D", 7)], "B": [("D", 5)], "C": [("D", 12)]}
        graph = astar.Graph()
        graph.init_with_friends(friends)
        path = graph.a_star_algorithm("A", "D")
        self.assertEqual(path, ["A", "B", "D"])

    def test_graph_construction(self):
        graph = astar.Graph()
        a = "A"
        b = "B"
        c = "C"
        graph.add(a, b, 1)
        self.assertEqual(graph.a_star_algorithm(a, b), ([a, b], 1))
        self.assertEqual(graph.a_star_algorithm(a, c), (None, math.inf))
        graph.add(b, c, 10)
        self.assertEqual(graph.a_star_algorithm(a, c), ([a, b, c], 11))
        graph.add(a, c, 2)
        self.assertEqual(graph.a_star_algorithm(a, c), ([a, c], 2))

    def test_graph_internet_tuples(self):
        astar.USE_TUPLE_IMPL = False
        friends = {"A": {"B": 1, "C": 3, "D": 7}, "B": {"D": 5}, "C": {"D": 12}}
        graph = astar.Graph()
        graph.init_with_friends(friends)
        path = graph.a_star_algorithm("A", "D")
        self.assertEqual(path, (["A", "B", "D"], 6))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
