#pragma once

#include <cmath>
#include <string>

class Point {
public:
  Point(float lat, float lon) : lat(lat), lon(lon){};
  std::string String() const {
    return "GPS(" + std::to_string(lat) + "," + std::to_string(lon) + ")";
  };
  float lat{};
  float lon{};
};

float Haversine(const Point &p1, const Point &p2) {
  float x = p2.lat - p1.lat;
  float y = (p2.lon - p1.lon) * std::cos((p2.lat + p1.lat) * 0.00872664626F);
  return 111.319F * std::sqrt(x * x + y * y);
}

float Distance(const Point &l, const Point &r) { return Haversine(l, r); }

bool operator<(const Point &l, const Point &r) { return Distance(l, r) < 0; }
