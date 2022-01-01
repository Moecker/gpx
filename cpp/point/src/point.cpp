#include "point.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(point, m) {
  py::class_<Point>(m, "Point")
      .def(py::init<float, float>())
      .def_readwrite("lat", &Point::lat)
      .def_readwrite("lon", &Point::lon);
}
