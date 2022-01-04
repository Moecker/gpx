#pragma once

#include "../../point/include/point.h"
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

using Hash = std::string;

class GraphHash {
public:
  GraphHash() {}

  void build_heuristic(const Point &);
  void build(std::unordered_map<std::string, std::vector<Hash>>);

  void add(const Point &, const Point &, int);
  void dump();
  void dump_keys();

  std::vector<Hash> keys();
  std::vector<Hash> nodes();
  std::vector<int> weights();

  Hash closest(const Point p);

  void adjust_weight(const Point, const Point, int);

  std::tuple<std::vector<const Point>, int> dijkstra(const Point &,
                                                     const Point &);
  std::tuple<std::vector<const Point>, int> find_shortest_path(const Point &,
                                                               const Point &);

  std::string string() const;
  Point get(Hash);

  std::vector<Hash> mock();

  std::unordered_map<Hash, int> heuristic{};
  std::unordered_map<Hash, std::unordered_map<Hash, int>> friends{};
  std::unordered_map<Hash, const Point> storage{};
};
