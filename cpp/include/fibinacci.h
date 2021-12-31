#include <pybind11/pybind11.h>

unsigned int fibinacci(const unsigned int n);

namespace py = pybind11;

PYBIND11_MODULE(fibinacci, mod)
{
    mod.def("fibinacci", &fibinacci, "Recursive fibinacci algorithm.");
}
