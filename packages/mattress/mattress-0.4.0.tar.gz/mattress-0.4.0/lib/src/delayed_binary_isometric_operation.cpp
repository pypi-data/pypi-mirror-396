#include "mattress.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include "tatami/tatami.hpp"

#include <string>
#include <cstdint>

std::uintptr_t initialize_delayed_binary_isometric_operation(std::uintptr_t left, std::uintptr_t right, const std::string& op) {
    std::shared_ptr<tatami::DelayedBinaryIsometricOperationHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex> > opptr;

    if (op == "add") {
        opptr.reset(new tatami::DelayedBinaryIsometricAddHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "subtract") {
        opptr.reset(new tatami::DelayedBinaryIsometricSubtractHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "multiply") {
        opptr.reset(new tatami::DelayedBinaryIsometricMultiplyHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "divide") {
        opptr.reset(new tatami::DelayedBinaryIsometricDivideHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "remainder") {
        opptr.reset(new tatami::DelayedBinaryIsometricModuloHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "floor_divide") {
        opptr.reset(new tatami::DelayedBinaryIsometricIntegerDivideHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "power") {
        opptr.reset(new tatami::DelayedBinaryIsometricPowerHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "equal") {
        opptr.reset(new tatami::DelayedBinaryIsometricEqualHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "not_equal") {
        opptr.reset(new tatami::DelayedBinaryIsometricNotEqualHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "greater") {
        opptr.reset(new tatami::DelayedBinaryIsometricGreaterThanHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "greater_equal") {
        opptr.reset(new tatami::DelayedBinaryIsometricGreaterThanOrEqualHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "less") {
        opptr.reset(new tatami::DelayedBinaryIsometricLessThanHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "less_equal") {
        opptr.reset(new tatami::DelayedBinaryIsometricLessThanOrEqualHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else if (op == "logical_and") {
        opptr.reset(new tatami::DelayedBinaryIsometricBooleanAndHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "logical_or") {
        opptr.reset(new tatami::DelayedBinaryIsometricBooleanOrHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);
    } else if (op == "logical_xor") {
        opptr.reset(new tatami::DelayedBinaryIsometricBooleanXorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>);

    } else {
        throw std::runtime_error("unknown binary isometric operation '" + op + "'");
    }

    auto lbound = mattress::cast(left);
    auto rbound = mattress::cast(right);
    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(
        new tatami::DelayedBinaryIsometricOperation<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(
            lbound->ptr,
            rbound->ptr,
            std::move(opptr)
        )
    );

    pybind11::tuple original(2);
    original[0] = lbound->original;
    original[1] = rbound->original;
    tmp->original = std::move(original);
    return mattress::cast(tmp.release());
}

void init_delayed_binary_isometric_operation(pybind11::module& m) {
    m.def("initialize_delayed_binary_isometric_operation", &initialize_delayed_binary_isometric_operation);
}
