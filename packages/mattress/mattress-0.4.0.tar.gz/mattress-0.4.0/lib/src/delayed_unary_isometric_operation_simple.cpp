#include "mattress.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include "tatami/tatami.hpp"

#include <string>
#include <cstdint>

std::uintptr_t initialize_delayed_unary_isometric_operation_simple(std::uintptr_t ptr, const std::string& op) {
    std::shared_ptr<tatami::DelayedUnaryIsometricOperationHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex> > opptr;

    if (op == "abs") {
        opptr.reset(new tatami::DelayedUnaryIsometricAbsHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "sign") {
        opptr.reset(new tatami::DelayedUnaryIsometricSignHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "log") {
        opptr.reset(new tatami::DelayedUnaryIsometricLogHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>);
    } else if (op == "log2") {
        opptr.reset(new tatami::DelayedUnaryIsometricLogHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(2.0));
    } else if (op == "log10") {
        opptr.reset(new tatami::DelayedUnaryIsometricLogHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(10.0));
    } else if (op == "log1p") {
        opptr.reset(new tatami::DelayedUnaryIsometricLog1pHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>);

    } else if (op == "sqrt") {
        opptr.reset(new tatami::DelayedUnaryIsometricSqrtHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "ceil") {
        opptr.reset(new tatami::DelayedUnaryIsometricCeilingHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "floor") {
        opptr.reset(new tatami::DelayedUnaryIsometricFloorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "trunc") {
        opptr.reset(new tatami::DelayedUnaryIsometricTruncHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "round") {
        opptr.reset(new tatami::DelayedUnaryIsometricRoundHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "exp") {
        opptr.reset(new tatami::DelayedUnaryIsometricExpHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "expm1") {
        opptr.reset(new tatami::DelayedUnaryIsometricExpm1Helper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "cos") {
        opptr.reset(new tatami::DelayedUnaryIsometricCosHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "sin") {
        opptr.reset(new tatami::DelayedUnaryIsometricSinHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "tan") {
        opptr.reset(new tatami::DelayedUnaryIsometricTanHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "cosh") {
        opptr.reset(new tatami::DelayedUnaryIsometricCoshHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "sinh") {
        opptr.reset(new tatami::DelayedUnaryIsometricSinhHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "tanh") {
        opptr.reset(new tatami::DelayedUnaryIsometricTanhHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "arccos") {
        opptr.reset(new tatami::DelayedUnaryIsometricAcosHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "arcsin") {
        opptr.reset(new tatami::DelayedUnaryIsometricAsinHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "arctan") {
        opptr.reset(new tatami::DelayedUnaryIsometricAtanHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "arccosh") {
        opptr.reset(new tatami::DelayedUnaryIsometricAcoshHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "arcsinh") {
        opptr.reset(new tatami::DelayedUnaryIsometricAsinhHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "arctanh") {
        opptr.reset(new tatami::DelayedUnaryIsometricAtanhHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else {
        throw std::runtime_error("unknown binary isometric operation '" + op + "'");
    }

    auto bound = mattress::cast(ptr);
    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(
        new tatami::DelayedUnaryIsometricOperation<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(
            bound->ptr,
            std::move(opptr)
        )
    );
    tmp->original = bound->original;
    return mattress::cast(tmp.release());
}

void init_delayed_unary_isometric_operation_simple(pybind11::module& m) {
    m.def("initialize_delayed_unary_isometric_operation_simple", &initialize_delayed_unary_isometric_operation_simple);
}
