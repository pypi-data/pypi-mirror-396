#include "mattress.h"

#include "pybind11/pybind11.h"
#include "tatami_python/tatami_python.hpp"

std::uintptr_t initialize_unknown_matrix(const pybind11::object& input, std::size_t cache_size) {
    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->original = input;
    tatami_python::UnknownMatrixOptions opt;
    opt.maximum_cache_size = cache_size;
    tmp->ptr.reset(new tatami_python::UnknownMatrix<mattress::MatrixValue, mattress::MatrixIndex>(input, opt));
    return mattress::cast(tmp.release());
}

void init_unknown_matrix(pybind11::module& m) {
    m.def("initialize_unknown_matrix", &initialize_unknown_matrix);
}
