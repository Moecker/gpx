#include "graph.h"

#include <iostream>
#include <sstream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

const Hash hash(const Point &p) {
  std::stringstream s{};
  s << p.latitude << ":" << p.longitude << ":" << p.annotation;
  return s.str();
}

Point GraphHash::get(Hash h) { return storage.find(h)->second; }

const Hash GraphHash::closest(const Point p) {
  Hash first;
  for (const auto &node : friends) {
    (void)node;
  }
  return first;
}

void GraphHash::build_heuristic(const Point &end) {
  heuristic.insert(std::make_pair(hash(end), 0));
}

std::vector<const Hash> GraphHash::keys() {
  std::vector<const Hash> keys;

  std::transform(
      friends.begin(), friends.end(), std::back_inserter(keys),
      [](const std::map<const Hash, std::map<const Hash, int>>::value_type
             &pair) { return pair.first; });
  return keys;
}

std::vector<const Hash> GraphHash::nodes() {
  std::vector<const Hash> nodes;

  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      nodes.push_back(neighbors.first);
    }
  }
  return nodes;
}

std::vector<int> GraphHash::weights() {
  std::vector<int> weights;

  for (const auto &node : friends) {
    for (const auto &neighbors : node.second) {
      weights.push_back(neighbors.second);
    }
  }
  return weights;
};

void GraphHash::adjust_weight(const Point p1, const Point p2,
                              int cost) { // TODO Implement
}

void GraphHash::build(std::map<std::string, std::vector<const Hash>>) {}

void GraphHash::add(const Point &p1, const Point &p2, int cost) {
  storage.insert(std::make_pair(hash(p1), p1));
  storage.insert(std::make_pair(hash(p2), p2));

  if (friends.find(hash(p1)) == friends.end()) {
    std::map<const Hash, int> forward{};
    forward.insert(std::make_pair(hash(p2), cost));
    friends.insert(std::make_pair(hash(p1), forward));
  } else {
    friends.find(hash(p1))->second.insert(std::make_pair(hash(p2), cost));
  }

  if (friends.find(hash(p2)) == friends.end()) {
    std::map<const Hash, int> forward{};
    forward.insert(std::make_pair(hash(p1), cost));
    friends.insert(std::make_pair(hash(p2), forward));
  } else {
    friends.find(hash(p2))->second.insert(std::make_pair(hash(p1), cost));
  }
}

std::tuple<std::vector<const Point>, int>
GraphHash::find_shortest_path(const Point &start, const Point &end) {
  std::map<const Hash, std::vector<const Hash>> dist{};
  std::vector<const Hash> start_path{};

  start_path.push_back(hash(start));
  dist.insert(std::make_pair(hash(start), start_path));

  std::deque<const Hash> q{};
  q.push_back(hash(start));

  while (q.size() > 0) {
    const Hash at = q.front();
    q.pop_front();

    if (friends.find(at) != friends.end()) {
      for (auto p : friends.find(at)->second) {
        if (dist.find(p.first) == dist.end()) {
          std::vector<const Hash> to_add = dist.find(at)->second;
          to_add.push_back(p.first);

          dist.insert(std::make_pair(p.first, to_add));
          q.push_back(p.first);
        } else {
        }
      }
    }
  }
  if (dist.find(hash(end)) != dist.end()) {
    std::vector<const Point> path{};
    auto path_hash = dist.find(hash(end))->second;
    for (const auto &p : path_hash) {
      path.push_back(get(p));
    }
    return std::make_tuple(path, 0);
  } else {
    return std::make_tuple(std::vector<const Point>{}, 0);
  }
}

std::tuple<std::vector<const Point>, int>
GraphHash::dijkstra(const Point &start, const Point &end) {
  return std::make_tuple(std::vector<const Point>{}, 0);
}

std::string GraphHash::string() const {
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

void GraphHash::dump() { std::cout << string(); }

void GraphHash::dump_keys() {
  for (const auto &key : friends) {
    std::cout << key.first << std::endl;
  }
}

namespace py = pybind11;

PYBIND11_MODULE(graph, m) {
  m.def("hash", &hash);

  py::class_<GraphHash>(m, "GraphHash", py::dynamic_attr())
      .def(py::init())
      .def("add", &GraphHash::add)
      .def("build", &GraphHash::build)
      .def("build_heuristic", &GraphHash::build_heuristic)
      .def("dump", &GraphHash::dump)
      .def("dump_keys", &GraphHash::dump_keys)
      .def("dijkstra", &GraphHash::dijkstra)
      .def("keys", &GraphHash::keys)
      .def("nodes", &GraphHash::nodes)
      .def("weights", &GraphHash::weights)
      .def("adjust_weight", &GraphHash::adjust_weight)
      .def("closest", &GraphHash::closest)
      .def("get", &GraphHash::get)
      .def("find_shortest_path", &GraphHash::find_shortest_path)
      .def("__str__", &GraphHash::string)
      .def("__repr__", &GraphHash::string)
      .def(py::pickle(
          [](const GraphHash &g) {
            return py::make_tuple(g.friends, g.storage);
          },
          [](py::tuple t) {
            if (t.size() != 2)
              throw std::runtime_error("Invalid state");

            GraphHash g{};

            g.friends =
                t[0].cast<std::map<const Hash, std::map<const Hash, int>>>();
            g.storage = t[1].cast<std::map<const Hash, const Point>>();

            return g;
          }));
}
