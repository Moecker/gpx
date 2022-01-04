#pragma once

#include "../../point/include/point.h"
#include <map>
#include <string>
#include <tuple>
#include <vector>

class Graph {
public:
  Graph() = default;

  void build_heuristic(const Point *);
  void build(std::map<std::string, std::vector<const Point *>>);

  void add(const Point *, const Point *, int);
  void dump();
  void dump_keys();

  std::vector<const Point *> keys();
  std::vector<const Point *> nodes();
  std::vector<int> weights();

  const Point *const closest(const Point p);

  void adjust_weight(const Point *, const Point *, int);

  std::tuple<std::vector<const Point *>, int> dijkstra(const Point *,
                                                       const Point *);
  std::string string() const;

  std::vector<const Point *> mock();

  std::map<const Point *, int> heuristic{};
  std::map<const Point *, std::map<const Point *, int>> friends{};

  std::map<const Point, std::map<const Point, int>> storage{};
};
