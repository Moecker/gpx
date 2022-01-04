#pragma once

#include "../../point/include/point.h"
#include <map>
#include <string>
#include <tuple>
#include <vector>

class Graph {
public:
  Graph() = default;

  void build_heuristic(Point *);
  void build(std::map<std::string, std::vector<Point *>>);

  void add(Point *, Point *, int);
  void dump();
  void dump_keys();

  std::vector<Point *> keys();
  std::vector<Point *> nodes();
  std::vector<int> weights();

  void adjust_weight(Point *, Point *, int);

  std::tuple<std::vector<Point *>, int> dijkstra(Point *, Point *);
  std::string string() const;

  std::map<Point *, int> heuristic{};
  std::map<Point *, std::map<Point *, int>> friends{};
};
