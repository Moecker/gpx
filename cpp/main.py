import point.point as point
import graph.graph as graph


g = graph.Graph()

p1 = point.Point(1.0, 2.0)
p2 = point.Point(3.0, 4.0)
p3 = point.Point(5.0, 6.0)

g.Add(p1, p2, 100)
g.Add(p1, p3, 450)
g.Add(p2, p3, 200)

print(g)
g.Dump()

# print(g.Find(p1, p2))
# print(g.Find(p1, p3))
# print(g.Find(p2, p3))

# print(point.Distance(p1, p2))
# print(point.Distance(p1, p3))

# print()
# g.Find(p1, p2)
# g.Find(p1, p3)
# g.Find(p3, p3)
