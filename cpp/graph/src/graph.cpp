#include "graph.h"

#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

void Graph::BuildHeuristic(Point end) { heuristic.insert(std::pair(end, 0)); }

void Graph::Build(std::map<std::string, std::vector<Point>>) {}

void Graph::Add(Point p1, Point p2, int cost) {
  std::map<Point, int> entry{};
  entry.insert(std::pair(p2, cost));
  friends.insert(std::pair(p1, entry));
}

void Graph::Dump() {
  for (auto node : friends) {
    for (auto neighbors : node.second) {
      std::cout << node.first.lat << "->" << neighbors.first.lat << ":"
                << neighbors.second << std::endl;
    }
  }
}

namespace py = pybind11;

PYBIND11_MODULE(graph, m) {
  py::class_<Graph>(m, "Graph")
      .def(py::init())
      .def("BuildHeuristic", &Graph::BuildHeuristic)
      .def("Build", &Graph::Build)
      .def("Dump", &Graph::Dump)
      .def("Add", &Graph::Add);
}
