#include <pybind11/pybind11.h>

unsigned int fibonacci(const unsigned int n);

namespace py = pybind11;

PYBIND11_MODULE(fibonacci, mod) {
  mod.def("fibonacci", &fibonacci, "Recursive fibonacci algorithm.");
}
