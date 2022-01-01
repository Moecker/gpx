import point.point as point
import graph.graph as graph


g = graph.Graph()

p1 = point.Point(1.0, 2.0)
p2 = point.Point(3.0, 4.0)
p3 = point.Point(5.0, 6.0)

g.Build({"first":[p1, p2], "second":[p3]})

g.Add(p1, p2, 100)
g.Add(p2, p3, 200)

g.Dump()
