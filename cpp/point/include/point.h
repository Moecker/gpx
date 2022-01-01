#pragma once

class Point {
public:
  Point(float lat, float lon) : lat(lat), lon(lon){};
  float lat{};
  float lon{};
};

bool operator<(const Point &l, const Point &r) { return true; }
