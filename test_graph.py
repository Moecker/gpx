import graph
import logging
import unittest


class TestGraph(unittest.TestCase):
    def test_graph_nodes_same_cost(self):
        # Foo --(1)--> Bar --(1)--> Ohm
        #  |___________(1)___________^
        g = graph.Graph()
        foo = "Foo"
        bar = "Bar"
        ohm = "Ohm"
        g.add(foo, bar, 1)
        g.add(bar, ohm, 1)
        self.assertEqual(g.find_shortest_path(foo, ohm), [foo, bar, ohm])
        self.assertEqual(g.dijkstra(foo, ohm), [foo, bar, ohm])
        g.add(foo, ohm, 1)
        self.assertEqual(g.find_shortest_path(foo, ohm), [foo, ohm])
        self.assertEqual(g.dijkstra(foo, ohm), [foo, ohm])

    def test_graph_three_different_cost(self):
        # Foo --(1)--> Bar --(1)--> Ohm
        #  |___________(1)___________^
        g = graph.Graph()
        foo = "Foo"
        bar = "Bar"
        ohm = "Ohm"
        g.add(foo, bar, 1)
        g.add(bar, ohm, 10)
        self.assertEqual(g.find_shortest_path(foo, ohm), [foo, bar, ohm])
        self.assertEqual(g.dijkstra(foo, ohm), [foo, bar, ohm])
        g.add(foo, ohm, 5)
        self.assertEqual(g.find_shortest_path(foo, ohm), [foo, ohm])
        self.assertEqual(g.dijkstra(foo, ohm), [foo, ohm])
        self.assertEqual(g.dijkstra(bar, ohm), [bar, foo, ohm])

    def test_internet(self):
        g = graph.Graph()

        edges = [
            ("X", "A", 7),
            ("X", "B", 2),
            ("X", "C", 3),
            ("X", "E", 4),
            ("A", "B", 3),
            ("A", "D", 4),
            ("B", "D", 4),
            ("B", "H", 5),
            ("C", "L", 2),
            ("D", "F", 1),
            ("F", "H", 3),
            ("G", "H", 2),
            ("G", "Y", 2),
            ("I", "J", 6),
            ("I", "K", 4),
            ("I", "L", 4),
            ("J", "L", 1),
            ("K", "Y", 5),
        ]

        for edge in edges:
            g.add(*edge)

        path = g.dijkstra("X", "Y")
        self.assertEqual(path, ["X", "B", "H", "G", "Y"])

    def test_nodes(self):
        g = graph.Graph()
        foo = "Foo"
        bar = "Bar"
        g.add(foo, bar, 1)
        self.assertEqual(len(g.nodes()), 2)
        self.assertEqual(g.nodes(), [bar, foo])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
