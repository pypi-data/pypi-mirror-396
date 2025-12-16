#include "mattress.h"
#include "utils.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <string>
#include <stdexcept>
#include <cstdint>

template<typename Data_, typename Index_>
std::uintptr_t initialize_compressed_sparse_matrix_raw(
    const mattress::MatrixIndex nr,
    const mattress::MatrixValue nc,
    const pybind11::array& data,
    const pybind11::array& index,
    const pybind11::array& indptr,
    const bool byrow
) {
    tatami::ArrayView<Data_> dview(check_contiguous_numpy_array<Data_>(data), sanisizer::cast<std::size_t>(data.size()));
    tatami::ArrayView<Index_> iview(check_contiguous_numpy_array<Index_>(index), sanisizer::cast<std::size_t>(index.size()));
    tatami::ArrayView<std::uint64_t> pview(check_numpy_array<std::uint64_t>(indptr), sanisizer::cast<std::size_t>(indptr.size()));

    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(
        new tatami::CompressedSparseMatrix<
            mattress::MatrixValue,
            mattress::MatrixIndex,
            I<decltype(dview)>,
            I<decltype(iview)>,
            I<decltype(pview)>
        >(
            nr,
            nc,
            std::move(dview),
            std::move(iview),
            std::move(pview),
            byrow,
            /* check = */ true
        )
    );

    pybind11::tuple objects(3);
    objects[0] = data;
    objects[1] = index;
    objects[2] = indptr;
    tmp->original = std::move(objects);

    return mattress::cast(tmp.release());
}

template<typename Data_>
std::uintptr_t initialize_compressed_sparse_matrix_itype(
    const mattress::MatrixIndex nr,
    const mattress::MatrixValue nc,
    const pybind11::array& data,
    const pybind11::array& index,
    const pybind11::array& indptr,
    const bool byrow
) {
    auto dtype = index.dtype();

    if (dtype.is(pybind11::dtype::of<std::int64_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::int64_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int32_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::int32_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int16_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::int16_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int8_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::int8_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint64_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::uint64_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint32_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::uint32_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint16_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::uint16_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint8_t>())) {
        return initialize_compressed_sparse_matrix_raw<Data_, std::uint8_t>(nr, nc, data, index, indptr, byrow);
    }

    throw std::runtime_error("unrecognized index type '" + std::string(dtype.kind(), 1) + std::to_string(dtype.itemsize()) + "' for compressed sparse matrix initialization");
    return 0;
}

std::uintptr_t initialize_compressed_sparse_matrix(
    const mattress::MatrixIndex nr,
    const mattress::MatrixValue nc,
    const pybind11::array& data,
    const pybind11::array& index,
    const pybind11::array& indptr,
    const bool byrow)
{
    auto dtype = data.dtype();

    if (dtype.is(pybind11::dtype::of<double>())) {
        return initialize_compressed_sparse_matrix_itype<double>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<float>())) {          
        return initialize_compressed_sparse_matrix_itype<float>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int64_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::int64_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int32_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::int32_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int16_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::int16_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::int8_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::int8_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint64_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::uint64_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint32_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::uint32_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint16_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::uint16_t>(nr, nc, data, index, indptr, byrow);

    } else if (dtype.is(pybind11::dtype::of<std::uint8_t>())) {
        return initialize_compressed_sparse_matrix_itype<std::uint8_t>(nr, nc, data, index, indptr, byrow);
    }

    throw std::runtime_error("unrecognized data type '" + std::string(dtype.kind(), 1) + std::to_string(dtype.itemsize()) + "' for compressed sparse matrix initialization");
    return 0;
}

void init_compressed_sparse_matrix(pybind11::module& m) {
    m.def("initialize_compressed_sparse_matrix", &initialize_compressed_sparse_matrix);
}
