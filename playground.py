import graph
import cost_graph
import logging


def main():
    g = cost_graph.CostGraph([])

    g.add("A", "B", 2)

    foo = "Foo"
    bar = "Bar"
    ohm = "Ohm"

    g.add(foo, bar, 1)
    g.add(bar, ohm, 10)
    g.add(foo, ohm, 1)

    print(g)
    print(g.find_shortest_path(foo, ohm))
    print(g.dijkstra(foo, ohm))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
