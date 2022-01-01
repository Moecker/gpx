#include "graph.h"

#include <pybind11/pybind11.h>

void Graph::BuildHeuristic(Point end) { heuristic.insert(std::pair(end, 0)); }

namespace py = pybind11;

PYBIND11_MODULE(graph, m) {
  py::class_<Graph>(m, "Graph")
      .def(py::init())
      .def("BuildHeuristic", &Graph::BuildHeuristic);
}
