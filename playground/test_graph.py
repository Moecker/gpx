import graph

g = graph.Graph([])

n1 = 1
n2 = 2
n3 = 3
n4 = 4
n5 = 5

g.add(n1, n2)
g.add(n2, n3)
g.add(n3, n5)
g.add(n4, n5)

print(g)

print(g.find_path_recursive(n1, n3))
print("###")
print(g.find_path_iterative(n1, n3))
print("###")
print(g.find_path_recursive(n1, n5))
print("###")
print(g.find_path_iterative(n1, n5))
