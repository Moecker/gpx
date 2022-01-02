#include "graph.h"

#include <iostream>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

void Graph::BuildHeuristic(Point end) { heuristic.insert(std::pair(end, 0)); }

void Graph::Build(std::map<std::string, std::vector<Point>>) {}

// void Graph::Add(Point p1, Point p2, int cost) {
//   std::map<Point, int> forward{};
//   std::map<Point, int> backward{};

//   forward.insert(std::pair(p2, cost));
//   backward.insert(std::pair(p1, cost));

//   friends.insert(std::pair(p1, forward));
//   friends.insert(std::pair(p2, backward));
// }

void Graph::Add(Point p1, Point p2, int cost) {
  if (friends.find(p1) == friends.end()) {
    std::cout << "First Addition" << std::endl;
    std::map<Point, int> forward{};
    forward.insert(std::pair(p2, cost));
    friends.insert(std::pair(p1, forward));
  } else {
    std::cout << "Available Addition" << std::endl;
    std::cout << p2.String() << std::endl;
    friends.find(p1)->second.insert(std::pair(p2, cost));
    std::cout << friends.find(p1)->second.find(p2)->second << std::endl;
  }
}

std::vector<Point> Graph::Find(Point start, Point end) {
  std::vector<Point> path{};

  std::map<Point, std::vector<Point>> dist{};
  std::vector<Point> where{};
  where.push_back(start);
  dist.insert(std::make_pair(start, where));

  std::deque<Point> q{};
  q.push_back(start);

  while (q.size() > 0) {
    Point at = q.front();
    q.pop_front();

    for (auto p : friends.find(at)->second) {
      std::cout << p.first.String() << std::endl;
      if (dist.find(p.first) != dist.end()) {
        std::cout << "Found" << std::endl;
      } else {
        std::cout << "Not Found" << std::endl;
      }
    }
    // for (const std::map<Point, int> next : friends.find(at)->second) {
    // if (dist.find(next) == dist.end()) {
    //   std::vector<Point> where{};
    //   where.push_back(dist.find(at)->second);
    //   where.push_back(next);
    //   dist.insert(std::make_pair(next, where));
    //   q.push_back(next);
    // }
    // }
  }

  return dist.find(start)->second;
}

std::string Graph::String() const {
  std::stringstream ret{};
  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      ret << node.first.String() << "->" << neighbors.first.String() << " : "
          << neighbors.second << std::endl;
    }
  }
  return ret.str();
}

void Graph::Dump() {
  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      std::cout << node.first.String() << "->" << neighbors.first.String()
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
