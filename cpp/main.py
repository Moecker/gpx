import point.point as point
import graph.graph as graph


g = graph.Graph()

p1 = point.Point(1.0, 2.0)
p2 = point.Point(3.0, 4.0)
p3 = point.Point(5.0, 6.0)
p4 = point.Point(7.0, 8.0)
p5 = point.Point(9.0, 10.0)

g.Add(p1, p2, 100)
g.Add(p1, p3, 450)
g.Add(p2, p3, 200)
g.Add(p2, p1, 220)
g.Add(p3, p4, 60)

print(g)

print(g.Find(p1, p2))
print(g.Find(p1, p3))
print(g.Find(p2, p3))

print(point.Distance(p1, p2))
print(point.Distance(p1, p3))

g.Find(p1, p2)
g.Find(p1, p3)

print(g.Find(p1, p4))
print(g.Find(p1, p1))
print(g.Find(p1, p5))
print(g.Find(p4, p2))
