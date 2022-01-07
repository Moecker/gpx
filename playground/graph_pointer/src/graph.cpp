#include "graph.h"

#include <iostream>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

const Point *const Graph::closest(const Point p) {
  for (const auto &node : friends) {
    return node.first;
  }
}

std::vector<const Point *> Graph::mock() {
  return std::vector<const Point *>{};
}

void Graph::build_heuristic(const Point *end) {
  heuristic.insert(std::make_pair(end, 0));
}

std::vector<const Point *> Graph::keys() {
  std::vector<const Point *> keys;

  std::transform(
      friends.begin(), friends.end(), std::back_inserter(keys),
      [](const std::map<const Point *, std::map<const Point *, int>>::value_type
             &pair) { return pair.first; });
  return keys;
}

std::vector<const Point *> Graph::nodes() {
  std::vector<const Point *> nodes;

  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      nodes.push_back(neighbors.first);
    }
  }
  return nodes;
}

std::vector<int> Graph::weights() {
  std::vector<int> weights;

  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      weights.push_back(neighbors.second);
    }
  }
  return weights;
};

void Graph::adjust_weight(const Point *p1, const Point *p2,
                          int cost) {
}

void Graph::build(std::map<std::string, std::vector<const Point *>>) {}

void Graph::add(const Point *p1, const Point *p2, int cost) {
  if (friends.find(p1) == friends.end()) {
    std::map<const Point *, int> forward{};
    forward.insert(std::make_pair(p2, cost));
    friends.insert(std::make_pair(p1, forward));
  } else {
    friends.find(p1)->second.insert(std::make_pair(p2, cost));
  }

  if (friends.find(p2) == friends.end()) {
    std::map<const Point *, int> forward{};
    forward.insert(std::make_pair(p1, cost));
    friends.insert(std::make_pair(p2, forward));
  } else {
    friends.find(p2)->second.insert(std::make_pair(p1, cost));
  }
}

std::tuple<std::vector<const Point *>, int> Graph::dijkstra(const Point *start,
                                                            const Point *end) {
  std::map<const Point *, std::vector<const Point *>> dist{};
  std::vector<const Point *> start_path{};

  start_path.push_back(start);
  dist.insert(std::make_pair(start, start_path));

  std::deque<const Point *> q{};
  q.push_back(start);

  while (q.size() > 0) {
    const Point *at = q.front();
    q.pop_front();

    if (friends.find(at) != friends.end()) {
      for (auto p : friends.find(at)->second) {
        if (dist.find(p.first) == dist.end()) {
          std::vector<const Point *> to_add = dist.find(at)->second;
          to_add.push_back(p.first);

          dist.insert(std::make_pair(p.first, to_add));
          q.push_back(p.first);
        } else {
        }
      }
    }
  }
  if (dist.find(end) != dist.end()) {
    return std::make_tuple(dist.find(end)->second, 0);
  } else {
    return std::make_tuple(std::vector<const Point *>{}, 0);
  }
}

std::string Graph::string() const {
  std::stringstream ret{};
  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      ret << node.first->string() << "->" << neighbors.first->string() << " : "
          << neighbors.second << std::endl;
    }
  }
  auto flush = ret.str();
  if (!flush.empty() && flush[flush.length() - 1] == '\n') {
    flush.erase(flush.length() - 1);
  }
  return flush;
}

void Graph::dump() { std::cout << string(); }

void Graph::dump_keys() {
  for (const auto &key : friends) {
    std::cout << key.first << std::endl;
  }
}

namespace py = pybind11;

PYBIND11_MODULE(graph, m) {
  py::class_<Graph>(m, "Graph", py::dynamic_attr())
      .def(py::init())
      .def("add", &Graph::add)
      .def("build", &Graph::build)
      .def("build_heuristic", &Graph::build_heuristic)
      .def("dump", &Graph::dump)
      .def("dump_keys", &Graph::dump_keys)
      .def("dijkstra", &Graph::dijkstra)
      .def("keys", &Graph::mock)
      .def("nodes", &Graph::mock)
      .def("weights", &Graph::weights)
      .def("adjust_weight", &Graph::adjust_weight)
      .def("closest", &Graph::closest)
      .def("__str__", &Graph::string)
      .def("__repr__", &Graph::string)
      .def_readwrite("friends", &Graph::friends)
      .def(py::pickle(
          [](const Graph &g) {
            // Build map with real points
            std::map<const Point, std::map<const Point, int>> storage{};

            for (const auto &node : g.friends) {
              std::map<const Point, int> inner{};

              for (const auto &neighbors : node.second) {
                inner.insert(
                    std::make_pair(*(neighbors.first), neighbors.second));
              }
              storage.insert(std::make_pair(*(node.first), inner));
            }

            return py::make_tuple(storage);
          },
          [](py::tuple t) {
            if (t.size() != 1)
              throw std::runtime_error("Invalid state");

            Graph g{};

            g.storage =
                t[0].cast<std::map<const Point, std::map<const Point, int>>>();

            // Build map with reference points
            for (const auto &node : g.storage) {
              std::map<const Point *, int> inner{};
              for (const auto &neighbors : node.second) {
                inner.insert(
                    std::make_pair(&(neighbors.first), neighbors.second));
              }
              g.friends.insert(std::make_pair(&(node.first), inner));
            }

            return g;
          }));
}
