#pragma once

#include "../../point/include/point.h"
#include <map>

class Graph {
public:
  Graph() = default;
  void BuildHeuristic(Point p);
  std::map<Point, int> heuristic{};
  std::map<Point, std::map<Point, int>> friends{};
};
