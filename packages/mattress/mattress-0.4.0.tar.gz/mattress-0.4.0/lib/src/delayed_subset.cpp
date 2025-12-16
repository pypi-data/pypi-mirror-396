#include "mattress.h"
#include "utils.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <string>
#include <cstdint>

std::uintptr_t initialize_delayed_subset(std::uintptr_t ptr, const pybind11::array& subset, const bool byrow) {
    auto bound = mattress::cast(ptr);
    auto sptr = check_numpy_array<mattress::MatrixIndex>(subset);

    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr = tatami::make_DelayedSubset(bound->ptr, tatami::ArrayView<mattress::MatrixIndex>(sptr, subset.size()), byrow);

    pybind11::tuple original(2);
    original[0] = bound->original;
    original[1] = subset;
    tmp->original = std::move(original);

    return mattress::cast(tmp.release());
}

void init_delayed_subset(pybind11::module& m) {
    m.def("initialize_delayed_subset", &initialize_delayed_subset);
}
