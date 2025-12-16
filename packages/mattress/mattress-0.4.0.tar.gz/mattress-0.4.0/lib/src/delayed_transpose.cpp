#include "mattress.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <string>
#include <cstdint>

std::uintptr_t initialize_delayed_transpose(std::uintptr_t ptr) {
    auto bound = mattress::cast(ptr);
    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr = tatami::make_DelayedTranspose(bound->ptr);
    tmp->original = bound->original;
    return mattress::cast(tmp.release());
}

void init_delayed_transpose(pybind11::module& m) {
    m.def("initialize_delayed_transpose", &initialize_delayed_transpose);
}
