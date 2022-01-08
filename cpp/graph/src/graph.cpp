#include "graph.h"

#include <iostream>
#include <sstream>
#include <unordered_map>
#include <algorithm>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

Hash hash(const Point &p) {
  std::stringstream s{};
  s << p.latitude << ":" << p.longitude << ":" << p.annotation;
  return s.str();
}

Point Graph::get(Hash h) { return storage.find(h)->second; }

void Graph::build_heuristic(const Point &end) {
  heuristic.insert(std::make_pair(hash(end), 0));
}

std::vector<Hash> Graph::keys() {
  std::vector<Hash> keys;

  std::transform(friends.begin(), friends.end(), std::back_inserter(keys),
                 [](const std::unordered_map<
                     Hash, std::unordered_map<Hash, int>>::value_type &pair) {
                   return pair.first;
                 });
  return keys;
}

std::vector<Hash> Graph::nodes() {
  std::vector<Hash> nodes;

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

void Graph::adjust_weight(const Point p1, const Point p2, int cost) {
  friends.find(hash(p1))->second.find(hash(p2))->second = cost;
}

void Graph::add(Point p1, Point p2, int cost) {
  storage.insert(std::make_pair(hash(p1), p1));
  storage.insert(std::make_pair(hash(p2), p2));

  if (friends.find(hash(p1)) == friends.end()) {
    std::unordered_map<Hash, int> forward{};
    forward.insert(std::make_pair(hash(p2), cost));
    friends.insert(std::make_pair(hash(p1), forward));
  } else {
    friends.find(hash(p1))->second.insert(std::make_pair(hash(p2), cost));
  }

  if (friends.find(hash(p2)) == friends.end()) {
    std::unordered_map<Hash, int> forward{};
    forward.insert(std::make_pair(hash(p1), cost));
    friends.insert(std::make_pair(hash(p2), forward));
  } else {
    friends.find(hash(p2))->second.insert(std::make_pair(hash(p1), cost));
  }
}

std::tuple<std::vector<Point>, int>
Graph::find_shortest_path(const Point &start, const Point &end) {
  std::unordered_map<Hash, std::vector<Hash>> dist{};
  std::vector<Hash> start_path{};

  start_path.push_back(hash(start));
  dist.insert(std::make_pair(hash(start), start_path));

  std::deque<Hash> q{};
  q.push_back(hash(start));

  while (q.size() > 0) {
    Hash at = q.front();
    q.pop_front();

    if (friends.find(at) != friends.end()) {
      for (auto p : friends.find(at)->second) {
        if (dist.find(p.first) == dist.end()) {
          std::vector<Hash> to_add = dist.find(at)->second;
          to_add.push_back(p.first);

          dist.insert(std::make_pair(p.first, to_add));
          q.push_back(p.first);
        } else {
        }
      }
    }
  }

  if (dist.find(hash(end)) != dist.end()) {
    std::vector<Point> path{};
    auto path_hash = dist.find(hash(end))->second;
    for (auto p : path_hash) {
      path.push_back(get(p));
    }
    return std::make_tuple(path, 0);
  } else {
    return std::make_tuple(std::vector<Point>{}, 0);
  }
}

std::tuple<std::vector<Point>, int> Graph::dijkstra(const Point &start,
                                                          const Point &end) {
  return find_shortest_path(start, end);
}

std::string Graph::string() const {
  std::stringstream ret{};
  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      ret << storage.find(node.first)->second.string() << "->"
          << storage.find(neighbors.first)->second.string() << "$"
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

namespace py = pybind11;

PYBIND11_MODULE(graph, m) {
  m.def("hash", &hash);

  py::class_<Graph>(m, "Graph", py::dynamic_attr())
      .def(py::init())
      .def("add", &Graph::add)
      .def("build_heuristic", &Graph::build_heuristic)
      .def("dump", &Graph::dump)
      .def("dijkstra", &Graph::dijkstra)
      .def("keys", &Graph::keys)
      .def("nodes", &Graph::nodes)
      .def("weights", &Graph::weights)
      .def("adjust_weight", &Graph::adjust_weight)
      .def("get", &Graph::get)
      .def("find_shortest_path", &Graph::find_shortest_path)
      .def("__str__", &Graph::string)
      .def("__repr__", &Graph::string)
      .def(py::pickle(
          [](const Graph &g) { return py::make_tuple(g.friends, g.storage); },
          [](py::tuple t) {
            if (t.size() != 2)
              throw std::runtime_error("Invalid state");

            Graph g{};

            g.friends = t[0].cast<
                std::unordered_map<Hash, std::unordered_map<Hash, int>>>();
            g.storage = t[1].cast<std::unordered_map<Hash, const Point>>();

            return g;
          }));
}
