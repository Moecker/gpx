import pickle
import os

import cpp.point.point as point
import cpp.graph.graph as graph
import gpx_tools

from pathlib import Path

Path("test/pickle").mkdir(parents=True, exist_ok=True)


g = graph.Graph()

p1 = point.Point(1.0, 2.0)
p2 = point.Point(3.0, 4.0)
p3 = point.Point(5.0, 6.0)
p4 = point.Point(7.0, 8.0)
p5 = point.Point(9.0, 10.0)

g.add(p1, p2, 100)
g.add(p1, p3, 450)
g.add(p2, p3, 200)
g.add(p2, p1, 220)
g.add(p3, p4, 60)

print(g)

print(g.dijkstra(p1, p2))
print(g.dijkstra(p1, p3))
print(g.dijkstra(p2, p3))

print(point.distance(p1, p2))
print(point.distance(p1, p3))

g.dijkstra(p1, p2)
g.dijkstra(p1, p3)

print(g.dijkstra(p1, p4))
print(g.dijkstra(p1, p1))
print(g.dijkstra(p1, p5))
print(g.dijkstra(p4, p2))

print(g.keys())
g.add(p5, p5, 160)
print(g.keys())

print(p1)
p1.annotation = "Annotation"

p1.dump()

with open(os.path.join("test", "pickle", "point.p"), "wb") as f:
    pickle.dump(p1, f)

with open(os.path.join("test", "pickle", "point.p"), "rb") as f:
    p1 = pickle.load(f)

p1.dump()

print(p1)

g2 = graph.Graph()
p21 = point.Point(21.0, 22.0)
p22 = point.Point(23.0, 24.0)
g2.add(p21, p22, 2100)
g2.add(p1, p21, 2100)
print(g2)
print(g2.dijkstra(p1, p21))
print(g2.keys())

path, cost = g2.dijkstra(p1, p21)
path[0].dump()
path[1].dump()

p21.dump()

with open(os.path.join("test", "pickle", "graph.p"), "wb") as f:
    pickle.dump(g2, f)

with open(os.path.join("test", "pickle", "graph.p"), "rb") as f:
    g2 = pickle.load(f)

p21.dump()

path = print(g2.dijkstra(p1, p21))

g2.build_heuristic(p21)

py_point = gpx_tools.SimplePoint((80, 90))
print(py_point)
cpp_point = point.Point(py_point.latitude, py_point.longitude)
print(cpp_point)

g2.build_heuristic(cpp_point)

g3 = graph.Graph()
p31 = point.Point(31.0, 32.0)
p32 = point.Point(33.0, 34.0)
p33 = point.Point(35.0, 36.0)
p34 = point.Point(37.0, 38.0)
g3.add(p31, p32, 3100)
g3.add(p31, p33, 3500)
g3.add(p32, p33, 3700)
g3.add(p34, p33, 3800)

print(g3.keys())
print(g3.nodes())
print(g3.weights())

g3.adjust_weight(p32, p33, 1)

print(g3)
with open(os.path.join("test", "pickle", "graph.p"), "wb") as f:
    pickle.dump(g3, f)

with open(os.path.join("test", "pickle", "graph.p"), "rb") as f:
    g3 = pickle.load(f)

print(g3)
print(g3.weights())

print(g3.nodes())
print(g3.keys())

g4 = graph.Graph()
p41 = point.Point(41.0, 42.0)
p42 = point.Point(43.0, 44.0)
g4.add(p41, p42, 4100)

g5 = graph.Graph()
p51 = point.Point(51.0, 52.0)
p52 = point.Point(53.0, 54.0)
g5.add(p51, p52, 50)
print(g5)
p51.annotation = "bar"
print(graph.hash(p51))

with open(os.path.join("test", "pickle", "graph.p"), "wb") as f:
    pickle.dump(g5, f)

with open(os.path.join("test", "pickle", "graph.p"), "rb") as f:
    g5 = pickle.load(f)
print(g5)

p53 = point.Point(55.0, 56.0)
g5.add(p51, p53, 80)
g5.add(p52, p53, 80)

print(g5.keys())
print(g5.nodes())

print(g5.find_shortest_path(p51, p53))
path = g5.find_shortest_path(p51, p53)
print(path)

g5.build_heuristic(p51)

print(path[0][0])
print(path[0][1])

g5.adjust_weight(p51, p53, 998877)
print(g5)
g5.adjust_weight(p51, p53, 778800)
print(g5)
