#include "mattress.h"
#include "utils.h"

#include "tatami/tatami.hpp"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <stdexcept>
#include <string>
#include <cstdint>

template<typename Type_>
std::uintptr_t initialize_dense_matrix_internal(const mattress::MatrixIndex nr, const mattress::MatrixIndex nc, const pybind11::array& buffer) {
    const auto expected = sanisizer::product<std::size_t>(nr, nc); // we'll eventually need this as a size_t in ArrayView(), so might as well.
    if (!sanisizer::is_equal(buffer.size(), expected)) {
        throw std::runtime_error("unexpected size for the dense matrix buffer");
    }

    auto flag = buffer.flags();
    bool byrow = false;
    if (flag & pybind11::array::c_style) {
        byrow = true;
    } else if (flag & pybind11::array::f_style) {
        byrow = false;
    } else {
        throw std::runtime_error("numpy array contents should be contiguous");
    }

    auto tmp = std::make_unique<mattress::BoundMatrix>();
    auto ptr = get_numpy_array_data<Type_>(buffer);
    tatami::ArrayView<Type_> view(ptr, expected);
    tmp->ptr.reset(new tatami::DenseMatrix<mattress::MatrixValue, mattress::MatrixIndex, I<decltype(view)> >(nr, nc, std::move(view), byrow));
    tmp->original = buffer;

    return mattress::cast(tmp.release());
}

std::uintptr_t initialize_dense_matrix(const mattress::MatrixIndex nr, const mattress::MatrixIndex nc, const pybind11::array& buffer) {
    // Don't make any kind of copy of buffer to coerce the type or storage
    // order, as this should be handled by the caller; we don't provide any
    // protection from GC for the arrays referenced by the views. 
    auto dtype = buffer.dtype();

    if (dtype.is(pybind11::dtype::of<double>())) {
        return initialize_dense_matrix_internal<double>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<float>())) {
        return initialize_dense_matrix_internal<float>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::int64_t>())) {
        return initialize_dense_matrix_internal<std::int64_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::int32_t>())) {
        return initialize_dense_matrix_internal<std::int32_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::int16_t>())) {
        return initialize_dense_matrix_internal<std::int16_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::int8_t>())) {
        return initialize_dense_matrix_internal<std::int8_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::uint64_t>())) {
        return initialize_dense_matrix_internal<std::uint64_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::uint32_t>())) {
        return initialize_dense_matrix_internal<std::uint32_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::uint16_t>())) {
        return initialize_dense_matrix_internal<std::uint16_t>(nr, nc, buffer);

    } else if (dtype.is(pybind11::dtype::of<std::uint8_t>())) {
        return initialize_dense_matrix_internal<std::uint8_t>(nr, nc, buffer);
    }

    throw std::runtime_error("unrecognized array type '" + std::string(dtype.kind(), 1) + std::to_string(dtype.itemsize()) + "' for dense matrix initialization");
    return 0;
}

void init_dense_matrix(pybind11::module& m) {
    m.def("initialize_dense_matrix", &initialize_dense_matrix);
}
