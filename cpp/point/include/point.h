#pragma once

#include <cmath>
#include <iostream>
#include <sstream>
#include <string>

class Point {
public:
  Point(float latitude, float longitude)
      : latitude(latitude), longitude(longitude){};

  std::string string() const {
    std::string post = annotation.size() ? ":" + annotation : "";
    return "CPP_GPS(" + std::to_string(latitude) + "," +
           std::to_string(longitude) + ")" + post;
  };

  void dump() const;

  float latitude{};
  float longitude{};

  std::string annotation{};
};

float haversine(const Point &p1, const Point &p2) {
  float x = p2.latitude - p1.latitude;
  float y = (p2.longitude - p1.longitude) *
            std::cos((p2.latitude + p1.latitude) * 0.00872664626F);
  return 111.319F * std::sqrt(x * x + y * y);
}

float distance(const Point &l, const Point &r) { return haversine(l, r); }

bool operator<(const Point &l, const Point &r) { return &l < &r; }
