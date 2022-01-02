#include "point.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(point, m) {
  m.def("Distance", &Distance);
  py::class_<Point>(m, "Point")
      .def(py::init<float, float>())
      .def_readwrite("lat", &Point::lat)
      .def_readwrite("lon", &Point::lon)
      .def("__str__", &Point::String)
      .def("__repr__", &Point::String);
}
