#include "mattress.h"
#include "utils.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include "tatami/tatami.hpp"

#include <string>
#include <cstdint>

template<bool right_>
void initialize_delayed_unary_isometric_operation_with_vector_internal(
    std::shared_ptr<tatami::DelayedUnaryIsometricOperationHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex> >& opptr,
    const std::string& op,
    bool by_row,
    tatami::ArrayView<mattress::MatrixValue> aview
) {
    if (op == "subtract") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricSubtractVectorHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "divide") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricDivideVectorHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "remainder") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricModuloVectorHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "floor_divide") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricIntegerDivideVectorHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "power") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricPowerVectorHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else {
        throw std::runtime_error("unknown unary isometric vector operation '" + op + "'");
    }
}

std::uintptr_t initialize_delayed_unary_isometric_operation_with_vector(std::uintptr_t ptr, const std::string& op, bool right, bool by_row, const pybind11::array& arg) {
    auto aptr = check_numpy_array<double>(arg);
    tatami::ArrayView<double> aview(aptr, sanisizer::cast<std::size_t>(arg.size()));
    std::shared_ptr<tatami::DelayedUnaryIsometricOperationHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex> > opptr;

    if (op == "add") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricAddVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "multiply") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricMultiplyVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "equal") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricEqualVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "not_equal") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricNotEqualVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if ((right && op == "greater") || (!right && op == "less")) {
        opptr.reset(
            new tatami::DelayedUnaryIsometricGreaterThanVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if ((right && op == "greater_equal") || (!right && op == "less_equal")) {
        opptr.reset(
            new tatami::DelayedUnaryIsometricGreaterThanOrEqualVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if ((right && op == "less") || (!right && op == "greater")) {
        opptr.reset(
            new tatami::DelayedUnaryIsometricLessThanVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if ((right && op == "less_equal") || (!right && op == "greater_equal")) {
        opptr.reset(
            new tatami::DelayedUnaryIsometricLessThanOrEqualVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "logical_and") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricBooleanAndVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "logical_or") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricBooleanOrVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else if (op == "logical_xor") {
        opptr.reset(
            new tatami::DelayedUnaryIsometricBooleanXorVectorHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, I<decltype(aview)> >(
                std::move(aview),
                by_row
            )
        );

    } else { 
        if (right) {
            initialize_delayed_unary_isometric_operation_with_vector_internal<true>(opptr, op, by_row, std::move(aview));
        } else {
            initialize_delayed_unary_isometric_operation_with_vector_internal<false>(opptr, op, by_row, std::move(aview));
        }
    }

    auto bound = mattress::cast(ptr);
    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(new tatami::DelayedUnaryIsometricOperation<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(bound->ptr, std::move(opptr)));
    pybind11::tuple original(2);
    original[0] = bound->original;
    original[1] = arg;
    tmp->original = std::move(original);
    return mattress::cast(tmp.release());
}

template<bool right_>
void initialize_delayed_unary_isometric_operation_with_scalar_internal(
    std::shared_ptr<tatami::DelayedUnaryIsometricOperationHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex> >& opptr,
    const std::string& op,
    double arg
) {
    if (op == "subtract") {
        opptr.reset(new tatami::DelayedUnaryIsometricSubtractScalarHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "divide") {
        opptr.reset(new tatami::DelayedUnaryIsometricDivideScalarHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "remainder") {
        opptr.reset(new tatami::DelayedUnaryIsometricModuloScalarHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "floor_divide") {
        opptr.reset(new tatami::DelayedUnaryIsometricIntegerDivideScalarHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "power") {
        opptr.reset(new tatami::DelayedUnaryIsometricPowerScalarHelper<right_, mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else {
        throw std::runtime_error("unknown unary isometric scalar operation '" + op + "'");
    }
}

std::uintptr_t initialize_delayed_unary_isometric_operation_with_scalar(std::uintptr_t ptr, const std::string& op, bool right, double arg) {
    std::shared_ptr<tatami::DelayedUnaryIsometricOperationHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex> > opptr;

    if (op == "add") {
        opptr.reset(new tatami::DelayedUnaryIsometricAddScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "multiply") {
        opptr.reset(new tatami::DelayedUnaryIsometricMultiplyScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "equal") {
        opptr.reset(new tatami::DelayedUnaryIsometricEqualScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "not_equal") {
        opptr.reset(new tatami::DelayedUnaryIsometricNotEqualScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if ((right && op == "greater") || (!right && op == "less")) {
        opptr.reset(new tatami::DelayedUnaryIsometricGreaterThanScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if ((right && op == "greater_equal") || (!right && op == "less_equal")) {
        opptr.reset(new tatami::DelayedUnaryIsometricGreaterThanOrEqualScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if ((right && op == "less") || (!right && op == "greater")) {
        opptr.reset(new tatami::DelayedUnaryIsometricLessThanScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if ((right && op == "less_equal") || (!right && op == "greater_equal")) {
        opptr.reset(new tatami::DelayedUnaryIsometricLessThanOrEqualScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex, double>(arg));

    } else if (op == "logical_and") {
        opptr.reset(new tatami::DelayedUnaryIsometricBooleanAndScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(arg));

    } else if (op == "logical_or") {
        opptr.reset(new tatami::DelayedUnaryIsometricBooleanOrScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(arg));

    } else if (op == "logical_xor") {
        opptr.reset(new tatami::DelayedUnaryIsometricBooleanXorScalarHelper<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(arg));

    } else {
        if (right) {
            initialize_delayed_unary_isometric_operation_with_scalar_internal<true>(opptr, op, arg);
        } else {
            initialize_delayed_unary_isometric_operation_with_scalar_internal<false>(opptr, op, arg);
        }
    }

    auto bound = mattress::cast(ptr);
    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(new tatami::DelayedUnaryIsometricOperation<mattress::MatrixValue, mattress::MatrixValue, mattress::MatrixIndex>(bound->ptr, std::move(opptr)));
    tmp->original = bound->original;
    return mattress::cast(tmp.release());
}

void init_delayed_unary_isometric_operation_with_args(pybind11::module& m) {
    m.def("initialize_delayed_unary_isometric_operation_with_vector", &initialize_delayed_unary_isometric_operation_with_vector);
    m.def("initialize_delayed_unary_isometric_operation_with_scalar", &initialize_delayed_unary_isometric_operation_with_scalar);
}
