#include "graph.h"

#include <iostream>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

void Graph::BuildHeuristic(Point *end) {
  heuristic.insert(std::make_pair(end, 0));
}

void Graph::Build(std::map<std::string, std::vector<Point *>>) {}

void Graph::Add(Point *p1, Point *p2, int cost) {
  if (friends.find(p1) == friends.end()) {
    std::map<Point *, int> forward{};
    forward.insert(std::make_pair(p2, cost));
    friends.insert(std::make_pair(p1, forward));
  } else {
    friends.find(p1)->second.insert(std::make_pair(p2, cost));
  }

  if (friends.find(p2) == friends.end()) {
    std::map<Point *, int> forward{};
    forward.insert(std::make_pair(p1, cost));
    friends.insert(std::make_pair(p2, forward));
  } else {
    friends.find(p2)->second.insert(std::make_pair(p1, cost));
  }
}

std::vector<Point *> Graph::Find(Point *start, Point *end) {
  std::vector<Point *> path{};

  std::map<Point *, std::vector<Point *>> dist{};
  std::vector<Point *> start_path{};

  start_path.push_back(start);
  dist.insert(std::make_pair(start, start_path));

  std::deque<Point *> q{};
  q.push_back(start);

  while (q.size() > 0) {
    Point *at = q.front();
    q.pop_front();

    if (friends.find(at) != friends.end()) {
      for (auto p : friends.find(at)->second) {
        if (dist.find(p.first) == dist.end()) {
          std::vector<Point *> to_add = dist.find(at)->second;
          to_add.push_back(p.first);

          dist.insert(std::make_pair(p.first, to_add));
          q.push_back(p.first);
        } else {
        }
      }
    }
  }
  if (dist.find(end) != dist.end()) {
    return dist.find(end)->second;
  } else {
    return std::vector<Point *>{};
  }
}

std::string Graph::String() const {
  std::stringstream ret{};
  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      ret << node.first->String() << "->" << neighbors.first->String() << " : "
          << neighbors.second << std::endl;
    }
  }
  return ret.str();
}

void Graph::Dump() {
  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      std::cout << node.first->String() << "->" << neighbors.first->String()
                << " : " << neighbors.second << std::endl;
    }
  }
}

namespace py = pybind11;

PYBIND11_MODULE(graph, m) {
  py::class_<Graph>(m, "Graph")
      .def(py::init())
      .def("Add", &Graph::Add)
      .def("Build", &Graph::Build)
      .def("BuildHeuristic", &Graph::BuildHeuristic)
      .def("Dump", &Graph::Dump)
      .def("Find", &Graph::Find)
      .def("__str__", &Graph::String)
      .def("__repr__", &Graph::String);
}
