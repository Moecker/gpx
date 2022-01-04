#pragma once

#include "../../point/include/point.h"
#include <map>
#include <string>
#include <tuple>
#include <vector>

using Hash = std::string;

class GraphHash {
public:
  GraphHash() = default;

  void build_heuristic(const Point &);
  void build(std::map<std::string, std::vector<const Hash>>);

  void add(const Point &, const Point &, int);
  void dump();
  void dump_keys();

  std::vector<const Hash> keys();
  std::vector<const Hash> nodes();
  std::vector<int> weights();

  const Hash closest(const Point p);

  void adjust_weight(const Point, const Point, int);

  std::tuple<std::vector<const Point>, int> dijkstra(const Point &,
                                                     const Point &);
  std::tuple<std::vector<const Point>, int> find_shortest_path(const Point &,
                                                               const Point &);

  std::string string() const;
  Point get(Hash);

  std::vector<const Hash> mock();

  std::map<const Hash, int> heuristic{};
  std::map<const Hash, std::map<const Hash, int>> friends{};
  std::map<const Hash, const Point> storage{};
};
