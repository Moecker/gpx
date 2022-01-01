#pragma once

#include "../../point/include/point.h"
#include <map>
#include <string>
#include <vector>

class Graph {
public:
  Graph() = default;
  void BuildHeuristic(Point);
  void Build(std::map<std::string, std::vector<Point>>);

  void Add(Point, Point, int);

  void Dump();

  std::map<Point, int> heuristic{};
  std::map<Point, std::map<Point, int>> friends{};
};
