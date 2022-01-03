#include "point.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(point, m) {
  m.def("distance", &distance);

  py::class_<Point>(m, "Point")
      .def(py::init<float, float>())
      .def_readwrite("latitude", &Point::latitude)
      .def_readwrite("longitude", &Point::longitude)
      .def_readwrite("annotation", &Point::annotation)
      .def("__str__", &Point::string)
      .def("__repr__", &Point::string)
      .def(py::pickle(
          [](const Point &p) {
            return py::make_tuple(p.latitude, p.longitude, p.annotation);
          },
          [](py::tuple t) {
            if (t.size() != 3)
              throw std::runtime_error("Invalid state");

            Point p(t[0].cast<float>(), t[1].cast<float>());
            p.annotation = t[2].cast<std::string>();

            return p;
          }));
}
