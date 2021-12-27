import graph


cost_graph = graph.CostGraph()
normal_graph = graph.Graph([])
graphs = [cost_graph, normal_graph]

print(cost_graph)
print(cost_graph._graph["A"])
print(cost_graph._graph["A"]["B"])

cost_graph.add("A", "B", 2)

print(cost_graph)
print(cost_graph._graph["A"])
print(cost_graph._graph["A"]["B"])

foo = "Foo"
bar = "Bar"
ohm = "Ohm"

for g in graphs:
    g.add(foo, bar, 2)
    g.add(bar, ohm, 30)
    g.add(foo, ohm, 10)

print(cost_graph)
print(cost_graph.find_shortest_path(foo, ohm))
print(cost_graph.dijkstra(foo, ohm))
