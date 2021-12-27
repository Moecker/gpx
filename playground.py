import graph


cost_graph = graph.CostGraph()
normal_graph = graph.Graph([])
graphs = [cost_graph, normal_graph]

n1 = "Foo"
n2 = "Bar"
n3 = "Ohm"
n4 = "Can"
n5 = "Kar"

for g in graphs:
    g.add(n1, n2, 1)
    g.add(n2, n3, 1)
    g.add(n3, n5, 1)
    g.add(n4, n5, 1)

    print(g)

    print(g.find_shortest_path(n1, n3))
