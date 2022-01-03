import pickle

import point.point as point
import graph.graph as graph


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

print(g.find(p1, p2))
print(g.find(p1, p3))
print(g.find(p2, p3))

print(point.distance(p1, p2))
print(point.distance(p1, p3))

g.find(p1, p2)
g.find(p1, p3)

print(g.find(p1, p4))
print(g.find(p1, p1))
print(g.find(p1, p5))
print(g.find(p4, p2))

print(g.keys())
g.add(p5, p5, 160)
print(g.keys())

print(p1)
p1.annotation = "Annotation"

with open("point.p", "wb") as f:
    pickle.dump(p1, f)

with open("point.p", "rb") as f:
    p1 = pickle.load(f)

print(p1)

g2 = graph.Graph()
p21 = point.Point(21.0, 22.0)
p22 = point.Point(23.0, 24.0)
g2.add(p21, p22, 2100)
g2.add(p1, p21, 2100)
print(g2)
print(g2.find(p1, p21))
print(g2.keys())

with open("graph.p", "wb") as f:
    pickle.dump(g2, f)

with open("graph.p", "rb") as f:
    g2 = pickle.load(f)

