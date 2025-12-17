#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/complex.h>
#include "tdscontrol/roots.hpp"
#include "tdscontrol/tds.hpp"

namespace nb = nanobind;

NB_MODULE(pytdscontrol, m) {
    m.doc() = "tds-control python bindings";

    nb::class_<tds::tds>(m, "tds")
        .def(nb::init<std::vector<double>, std::vector<double>>(),
             "A", "hA")
        .def_prop_ro("mA", &tds::tds::mA)
        .def_prop_ro("n", &tds::tds::n);
    
    m.def("roots", &tds::roots, "Compute roots for a tds system");
}