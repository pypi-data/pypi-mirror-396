#include "mattress.h"
#include "utils.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <string>
#include <stdexcept>
#include <cstdint>

template<typename Data_, typename Index_>
std::uintptr_t initialize_fragmented_sparse_matrix_raw(
    const mattress::MatrixIndex nr,
    const mattress::MatrixValue nc,
    const pybind11::list& data,
    const pybind11::list& indices,
    const bool byrow
) {
    const auto nvec = byrow ? nr : nc;
    std::vector<tatami::ArrayView<Data_> > data_vec;
    data_vec.reserve(nvec);
    std::vector<tatami::ArrayView<Index_> > idx_vec;
    idx_vec.reserve(nvec);

    for (I<decltype(nvec)> i = 0; i < nvec; ++i) {
        auto curdata = data[i];
        if (pybind11::isinstance<pybind11::none>(curdata)) {
            data_vec.emplace_back(static_cast<Data_*>(NULL), 0);
            idx_vec.emplace_back(static_cast<Index_*>(NULL), 0);
            continue;
        }

        // This better not involve any copies.
        auto castdata = curdata.cast<pybind11::array>();
        auto castidx = indices[i].cast<pybind11::array>();
        data_vec.emplace_back(check_numpy_array<Data_>(castdata), sanisizer::cast<std::size_t>(castdata.size()));
        idx_vec.emplace_back(check_numpy_array<Index_>(castidx), sanisizer::cast<std::size_t>(castidx.size()));
    }

    auto tmp = std::make_unique<mattress::BoundMatrix>();
    tmp->ptr.reset(
        new tatami::FragmentedSparseMatrix<mattress::MatrixValue, mattress::MatrixIndex, I<decltype(data_vec)>, I<decltype(idx_vec)> >( 
            nr,
            nc,
            std::move(data_vec),
            std::move(idx_vec),
            byrow,
            /* check = */ true 
        )
    );

    pybind11::tuple original(2);
    original[0] = data;
    original[1] = indices;
    tmp->original = std::move(original);

    return mattress::cast(tmp.release());
}

template<typename Data_>
std::uintptr_t initialize_fragmented_sparse_matrix_itype(
    const mattress::MatrixIndex nr,
    const mattress::MatrixValue nc,
    const pybind11::list& data,
    const pybind11::list& indices,
    const bool byrow,
    const pybind11::dtype& index_type
) {
    if (index_type.is(pybind11::dtype::of<std::int64_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::int64_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::int32_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::int32_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::int16_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::int16_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::int8_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::int8_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::uint64_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::uint64_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::uint32_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::uint32_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::uint16_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::uint16_t>(nr, nc, data, indices, byrow);

    } else if (index_type.is(pybind11::dtype::of<std::uint8_t>())) {
        return initialize_fragmented_sparse_matrix_raw<Data_, std::uint8_t>(nr, nc, data, indices, byrow);
    }

    throw std::runtime_error("unrecognized index type '" + std::string(index_type.kind(), 1) + std::to_string(index_type.itemsize()) + "' for fragmented sparse matrix initialization");
    return 0;
}

std::uintptr_t initialize_fragmented_sparse_matrix(
    const mattress::MatrixIndex nr,
    const mattress::MatrixValue nc,
    const pybind11::list& data,
    const pybind11::list& indices,
    const bool byrow,
    const pybind11::dtype& data_type,
    const pybind11::dtype& index_type
) {
    if (data_type.is(pybind11::dtype::of<double>())) {
        return initialize_fragmented_sparse_matrix_itype<double>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<float>())) {
        return initialize_fragmented_sparse_matrix_itype<float>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::int64_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::int64_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::int32_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::int32_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::int16_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::int16_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::int8_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::int8_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::uint64_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::uint64_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::uint32_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::uint32_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::uint16_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::uint16_t>(nr, nc, data, indices, byrow, index_type);

    } else if (data_type.is(pybind11::dtype::of<std::uint8_t>())) {
        return initialize_fragmented_sparse_matrix_itype<std::uint8_t>(nr, nc, data, indices, byrow, index_type);
    }

    throw std::runtime_error("unrecognized data type '" + std::string(data_type.kind(), 1) + std::to_string(data_type.itemsize()) + "' for fragmented sparse matrix initialization");
    return 0;
}

void init_fragmented_sparse_matrix(pybind11::module& m) {
    m.def("initialize_fragmented_sparse_matrix", &initialize_fragmented_sparse_matrix);
}
