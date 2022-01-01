#pragma once

#include "../../point/include/point.h"
#include <map>

class Graph {
public:
  Graph() = default;
  void BuildHeuristic(Point p);

private:
  std::map<Point, int> heuristic_{};
  std::map<Point, std::map<Point, int>> friends_{};
};
