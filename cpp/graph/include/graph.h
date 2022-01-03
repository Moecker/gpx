#pragma once

#include "../../point/include/point.h"
#include <map>
#include <string>
#include <vector>

class Graph {
public:
  Graph() = default;

  void build_heuristic(Point *);
  void build(std::map<std::string, std::vector<Point *>>);

  void add(Point *, Point *, int);
  void dump();

  std::vector<Point *> keys();

  std::vector<Point *> find(Point *, Point *);
  std::string string() const;

  std::map<Point *, int> heuristic{};
  std::map<Point *, std::map<Point *, int>> friends{};
};
