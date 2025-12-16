#include "mattress.h"
#include "utils.h"

#include "tatami/tatami.hpp"

#include "pybind11/pybind11.h"

#include <vector>

std::uintptr_t initialize_delayed_bind(const pybind11::list& inputs, int along) {
    const auto nmats = inputs.size();
    auto combined = sanisizer::create<std::vector<std::shared_ptr<tatami::Matrix<mattress::MatrixValue, mattress::MatrixIndex> > > >(nmats);
    auto originals = sanisizer::create<pybind11::tuple>(inputs.size());

    for (I<decltype(nmats)> i = 0; i < nmats; ++i) {
        auto bound = mattress::cast(inputs[i].cast<std::uintptr_t>());
        combined[i] = bound->ptr;
        originals[i] = bound->original; 
    }

    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(new tatami::DelayedBind<mattress::MatrixValue, mattress::MatrixIndex>(std::move(combined), along == 0));
    tmp->original = std::move(originals);
    return mattress::cast(tmp.release());
}

void init_delayed_bind(pybind11::module& m) {
    m.def("initialize_delayed_bind", &initialize_delayed_bind);
}
