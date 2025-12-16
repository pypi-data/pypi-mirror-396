#include "mattress.h"
#include "utils.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

#include <cstddef>
#include <cstdint>

#include "tatami_stats/tatami_stats.hpp"

void free_mattress(std::uintptr_t ptr) {
    delete mattress::cast(ptr);
}

pybind11::tuple get_dim(std::uintptr_t ptr) {
    const auto& mat = mattress::cast(ptr)->ptr;
    pybind11::tuple output(2);
    output[0] = mat->nrow();
    output[1] = mat->ncol();
    return output;
}

bool get_sparse(std::uintptr_t ptr) {
    const auto& mat = mattress::cast(ptr)->ptr;
    return mat->is_sparse();
}

pybind11::array_t<mattress::MatrixValue> extract_row(std::uintptr_t ptr, mattress::MatrixIndex r) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    auto ext = tatami::consecutive_extractor<false, mattress::MatrixValue, mattress::MatrixIndex>(*mat, true, r, 1);
    auto out = ext->fetch(optr);
    tatami::copy_n(out, output.size(), optr);
    return output;
}

pybind11::array_t<mattress::MatrixValue> extract_column(uintptr_t ptr, mattress::MatrixIndex c) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    auto ext = tatami::consecutive_extractor<false, mattress::MatrixValue, mattress::MatrixIndex>(*mat, false, c, 1);
    auto out = ext->fetch(optr);
    tatami::copy_n(out, output.size(), optr);
    return output;
}

/** Stats **/

pybind11::array_t<mattress::MatrixValue> compute_column_sums(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::sums::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::sums::apply(false, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_sums(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::sums::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::sums::apply(true, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_variances(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::variances::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::variances::apply(false, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_variances(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::variances::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::variances::apply(true, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_medians(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::medians::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::medians::apply(false, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_medians(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::medians::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::medians::apply(true, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_mins(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::ranges::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::ranges::apply(false, *mat, optr, static_cast<mattress::MatrixValue*>(NULL), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_mins(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::ranges::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::ranges::apply(true, *mat, optr, static_cast<mattress::MatrixValue*>(NULL), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_maxs(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::ranges::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::ranges::apply(false, *mat, static_cast<mattress::MatrixValue*>(NULL), optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_maxs(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    const auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami_stats::ranges::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::ranges::apply(true, *mat, static_cast<mattress::MatrixValue*>(NULL), optr, opt);
    return output;
}

pybind11::tuple compute_row_ranges(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto mnout = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    auto mxout = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->nrow());
    const auto mnptr = static_cast<mattress::MatrixValue*>(mnout.request().ptr);
    const auto mxptr = static_cast<mattress::MatrixValue*>(mxout.request().ptr);

    tatami_stats::ranges::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::ranges::apply(true, *mat, mnptr, mxptr, opt);

    pybind11::tuple output(2);
    output[0] = mnout;
    output[1] = mxout;
    return output;
}

pybind11::tuple compute_column_ranges(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto mnout = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    auto mxout = sanisizer::create<pybind11::array_t<mattress::MatrixValue> >(mat->ncol());
    const auto mnptr = static_cast<mattress::MatrixValue*>(mnout.request().ptr);
    const auto mxptr = static_cast<mattress::MatrixValue*>(mxout.request().ptr);

    tatami_stats::ranges::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::ranges::apply(false, *mat, mnptr, mxptr, opt);

    pybind11::tuple output(2);
    output[0] = mnout;
    output[1] = mxout;
    return output;
}

pybind11::array_t<mattress::MatrixIndex> compute_row_nan_counts(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixIndex> >(mat->nrow());
    const auto optr = static_cast<mattress::MatrixIndex*>(output.request().ptr);
    tatami_stats::counts::nan::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::counts::nan::apply(true, *mat, optr, opt);
    return output;
}

pybind11::array_t<mattress::MatrixIndex> compute_column_nan_counts(std::uintptr_t ptr, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    auto output = sanisizer::create<pybind11::array_t<mattress::MatrixIndex> >(mat->ncol());
    const auto optr = static_cast<mattress::MatrixIndex*>(output.request().ptr);
    tatami_stats::counts::nan::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::counts::nan::apply(false, *mat, optr, opt);
    return output;
}

/** Grouped stats **/

typedef pybind11::array_t<mattress::MatrixValue, pybind11::array::f_style> ColumnMajorMatrix;

template<typename Rows_, typename Columns_>
ColumnMajorMatrix allocate_output_matrix(Rows_ nrow, Columns_ ncol) {
    sanisizer::product<I<decltype(std::declval<ColumnMajorMatrix>().size())> >(nrow, ncol); // check that this allocation doesn't overflow pybind's internal size_type.
    return ColumnMajorMatrix({ static_cast<std::size_t>(nrow), static_cast<std::size_t>(ncol) });
}

template<typename Rows_, typename Columns_>
auto allocate_output_ptrs(ColumnMajorMatrix& x, Rows_ nrow, Columns_ ncol) {
    sanisizer::product<std::size_t>(nrow, ncol); // check that this allocation doesn't overflow when accessed by raw pointers.
    const auto xptr = static_cast<mattress::MatrixValue*>(x.request().ptr);
    auto ptrs = sanisizer::create<std::vector<mattress::MatrixValue*> >(ncol);
    for (I<decltype(ncol)> c = 0; c < ncol; ++c) {
        ptrs[c] = xptr + sanisizer::product_unsafe<std::size_t>(c, nrow);
    }
    return ptrs;
}

pybind11::array_t<mattress::MatrixValue> compute_row_sums_by_group(std::uintptr_t ptr, const pybind11::array& grouping, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    const auto nrow = mat->nrow();
    const auto ncol = mat->ncol();

    const auto gptr = check_numpy_array<mattress::MatrixIndex>(grouping);
    if (!sanisizer::is_equal(grouping.size(), ncol)) {
        throw std::runtime_error("'grouping' should have length equal to the number of columns");
    }

    const auto ngroups = tatami_stats::total_groups(gptr, ncol);
    auto output = allocate_output_matrix(nrow, ngroups);
    auto ptrs = allocate_output_ptrs(output, nrow, ngroups);

    tatami_stats::grouped_sums::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::grouped_sums::apply(true, *mat, gptr, ngroups, ptrs.data(), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_sums_by_group(std::uintptr_t ptr, const pybind11::array& grouping, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    const auto nrow = mat->nrow();
    const auto ncol = mat->ncol();

    auto gptr = check_numpy_array<mattress::MatrixIndex>(grouping);
    if (!sanisizer::is_equal(grouping.size(), nrow)) {
        throw std::runtime_error("'grouping' should have length equal to the number of rows");
    }

    const auto ngroups = tatami_stats::total_groups(gptr, nrow);
    auto output = allocate_output_matrix(ncol, ngroups);
    auto ptrs = allocate_output_ptrs(output, ncol, ngroups);

    tatami_stats::grouped_sums::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::grouped_sums::apply(false, *mat, gptr, ngroups, ptrs.data(), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_variances_by_group(std::uintptr_t ptr, const pybind11::array_t<mattress::MatrixIndex>& grouping, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    const auto ncol = mat->ncol();

    const auto gptr = check_numpy_array<mattress::MatrixIndex>(grouping);
    if (!sanisizer::is_equal(grouping.size(), ncol)) {
        throw std::runtime_error("'grouping' should have length equal to the number of columns");
    }

    const auto group_sizes = tatami_stats::tabulate_groups<mattress::MatrixIndex, mattress::MatrixIndex>(gptr, ncol);
    const auto ngroups = group_sizes.size();
    auto output = allocate_output_matrix(ncol, ngroups);
    auto ptrs = allocate_output_ptrs(output, ncol, ngroups);

    tatami_stats::grouped_variances::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::grouped_variances::apply(true, *mat, gptr, ngroups, group_sizes.data(), ptrs.data(), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_variances_by_group(std::uintptr_t ptr, const pybind11::array_t<mattress::MatrixIndex>& grouping, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    const auto nrow = mat->nrow();
    const auto ncol = mat->ncol();

    const auto gptr = check_numpy_array<mattress::MatrixIndex>(grouping);
    if (!sanisizer::is_equal(grouping.size(), nrow)) {
        throw std::runtime_error("'grouping' should have length equal to the number of rows");
    }

    const auto group_sizes = tatami_stats::tabulate_groups<mattress::MatrixIndex, mattress::MatrixIndex>(gptr, nrow);
    const auto ngroups = group_sizes.size();
    auto output = allocate_output_matrix(ncol, ngroups);
    auto ptrs = allocate_output_ptrs(output, ncol, ngroups);

    tatami_stats::grouped_variances::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::grouped_variances::apply(false, *mat, grouping.data(), ngroups, group_sizes.data(), ptrs.data(), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_row_medians_by_group(std::uintptr_t ptr, const pybind11::array_t<mattress::MatrixIndex>& grouping, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    const auto ncol = mat->ncol();
    const auto nrow = mat->nrow();

    auto gptr = check_numpy_array<mattress::MatrixIndex>(grouping);
    if (!sanisizer::is_equal(grouping.size(), ncol)) {
        throw std::runtime_error("'grouping' should have length equal to the number of columns");
    }

    const auto group_sizes = tatami_stats::tabulate_groups<mattress::MatrixIndex, mattress::MatrixIndex>(gptr, ncol);
    const auto ngroups = group_sizes.size();
    auto output = allocate_output_matrix(nrow, ngroups);
    auto ptrs = allocate_output_ptrs(output, nrow, ngroups);

    tatami_stats::grouped_medians::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::grouped_medians::apply(true, *mat, gptr, group_sizes, ptrs.data(), opt);
    return output;
}

pybind11::array_t<mattress::MatrixValue> compute_column_medians_by_group(std::uintptr_t ptr, const pybind11::array_t<mattress::MatrixIndex>& grouping, int num_threads) {
    const auto& mat = mattress::cast(ptr)->ptr;
    const auto nrow = mat->nrow();
    const auto ncol = mat->ncol();

    auto gptr = check_numpy_array<mattress::MatrixIndex>(grouping);
    if (!sanisizer::is_equal(grouping.size(), nrow)) {
        throw std::runtime_error("'grouping' should have length equal to the number of rows");
    }

    auto group_sizes = tatami_stats::tabulate_groups<mattress::MatrixIndex, mattress::MatrixIndex>(gptr, nrow);
    const auto ngroups = group_sizes.size();
    auto output = allocate_output_matrix(ncol, ngroups);
    auto ptrs = allocate_output_ptrs(output, ncol, ngroups);

    tatami_stats::grouped_medians::Options opt;
    opt.num_threads = num_threads;
    tatami_stats::grouped_medians::apply(false, *mat, gptr, group_sizes, ptrs.data(), opt);
    return output;
}

/** Extraction **/

pybind11::array_t<mattress::MatrixValue> extract_dense_subset(std::uintptr_t ptr, bool row_noop, const pybind11::array& row_sub, bool col_noop, const pybind11::array& col_sub) {
    auto mat = mattress::cast(ptr)->ptr;

    if (!row_noop) {
        auto rptr = check_numpy_array<mattress::MatrixIndex>(row_sub);
        auto tmp = tatami::make_DelayedSubset<0>(std::move(mat), tatami::ArrayView<mattress::MatrixIndex>(rptr, row_sub.size()));
        mat.swap(tmp);
    }

    if (!col_noop) {
        auto cptr = check_numpy_array<mattress::MatrixIndex>(col_sub);
        auto tmp = tatami::make_DelayedSubset<1>(std::move(mat), tatami::ArrayView<mattress::MatrixIndex>(cptr, col_sub.size()));
        mat.swap(tmp);
    }

    const auto NR = mat->nrow(), NC = mat->ncol();
    auto output = allocate_output_matrix(NR, NC);
    auto optr = static_cast<mattress::MatrixValue*>(output.request().ptr);
    tatami::convert_to_dense(*mat, false, optr, tatami::ConvertToDenseOptions{});
    return output;
}

pybind11::object extract_sparse_subset(std::uintptr_t ptr, bool row_noop, const pybind11::array& row_sub, bool col_noop, const pybind11::array& col_sub) {
    auto mat = mattress::cast(ptr)->ptr;

    if (!row_noop) {
        auto rptr = check_numpy_array<mattress::MatrixIndex>(row_sub);
        auto tmp = tatami::make_DelayedSubset<0>(std::move(mat), tatami::ArrayView<mattress::MatrixIndex>(rptr, row_sub.size()));
        mat.swap(tmp);
    }

    if (!col_noop) {
        auto cptr = check_numpy_array<mattress::MatrixIndex>(col_sub);
        auto tmp = tatami::make_DelayedSubset<1>(std::move(mat), tatami::ArrayView<mattress::MatrixIndex>(cptr, col_sub.size()));
        mat.swap(tmp);
    }

    const auto NR = mat->nrow(), NC = mat->ncol();
    auto content = sanisizer::create<pybind11::list>(NC);
    if (mat->prefer_rows()) {
        auto vcollection = sanisizer::create<std::vector<std::vector<mattress::MatrixValue> > >(NC);
        auto icollection = sanisizer::create<std::vector<std::vector<mattress::MatrixIndex> > >(NC);
        sanisizer::cast<I<decltype(vcollection.front().size())> >(NR);
        sanisizer::cast<I<decltype(icollection.front().size())> >(NR);

        auto ext = tatami::consecutive_extractor<true, mattress::MatrixValue, mattress::MatrixIndex>(*mat, true, 0, NR);
        auto vbuffer = sanisizer::create<std::vector<mattress::MatrixValue> >(NC);
        auto ibuffer = sanisizer::create<std::vector<mattress::MatrixIndex> >(NC);

        for (I<decltype(NR)> r = 0; r < NR; ++r) {
            const auto info = ext->fetch(vbuffer.data(), ibuffer.data());
            for (I<decltype(info.number)> i = 0; i < info.number; ++i) {
                const auto c = info.index[i];
                vcollection[c].push_back(info.value[i]);
                icollection[c].push_back(r);
            }
        }

        for (I<decltype(NC)> c = 0; c < NC; ++c) {
            if (vcollection[c].size()) {
                pybind11::list tmp(2);
                tmp[0] = pybind11::array_t<mattress::MatrixIndex>(icollection[c].size(), icollection[c].data());
                tmp[1] = pybind11::array_t<mattress::MatrixValue>(vcollection[c].size(), vcollection[c].data());
                content[c] = std::move(tmp);
            } else {
                content[c] = pybind11::none();
            }
        }

    } else {
        auto ext = tatami::consecutive_extractor<true, mattress::MatrixValue, mattress::MatrixIndex>(*mat, false, 0, NC);
        auto vbuffer = sanisizer::create<std::vector<mattress::MatrixValue> >(NC);
        auto ibuffer = sanisizer::create<std::vector<mattress::MatrixIndex> >(NC);

        for (I<decltype(NC)> c = 0; c < NC; ++c) {
            auto info = ext->fetch(vbuffer.data(), ibuffer.data());
            if (info.number) {
                pybind11::list tmp(2);
                tmp[0] = pybind11::array_t<mattress::MatrixIndex>(info.number, info.index);
                tmp[1] = pybind11::array_t<mattress::MatrixValue>(info.number, info.value);
                content[c] = std::move(tmp);
            } else {
                content[c] = pybind11::none();
            }
        }
    }

    pybind11::tuple shape(2);
    shape[0] = NR;
    shape[1] = NC;
    pybind11::module bu = pybind11::module::import("delayedarray");
    return bu.attr("SparseNdarray")(shape, content, pybind11::dtype("float64"), pybind11::dtype("uint32"), false, false);
}

void init_common(pybind11::module& m) {
    m.def("free_mattress", &free_mattress);

    m.def("get_dim", &get_dim);
    m.def("get_sparse", &get_sparse);

    m.def("extract_row", &extract_row);
    m.def("extract_column", &extract_column);

    m.def("compute_column_sums", &compute_column_sums);
    m.def("compute_row_sums", &compute_row_sums);
    m.def("compute_column_variances", &compute_column_variances);
    m.def("compute_row_variances", &compute_row_variances);
    m.def("compute_column_medians", &compute_column_medians);
    m.def("compute_row_medians", &compute_row_medians);
    m.def("compute_column_mins", &compute_column_mins);
    m.def("compute_row_mins", &compute_row_mins);
    m.def("compute_column_maxs", &compute_column_maxs);
    m.def("compute_row_maxs", &compute_row_maxs);
    m.def("compute_column_ranges", &compute_column_ranges);
    m.def("compute_row_ranges", &compute_row_ranges);
    m.def("compute_column_nan_counts", &compute_column_nan_counts);
    m.def("compute_row_nan_counts", &compute_row_nan_counts);

    m.def("compute_row_sums_by_group", &compute_row_sums_by_group);
    m.def("compute_column_sums_by_group", &compute_column_sums_by_group);
    m.def("compute_row_variances_by_group", &compute_row_variances_by_group);
    m.def("compute_column_variances_by_group", &compute_column_variances_by_group);
    m.def("compute_row_medians_by_group", &compute_row_medians_by_group);
    m.def("compute_column_medians_by_group", &compute_column_medians_by_group);

    m.def("extract_dense_subset", &extract_dense_subset);
    m.def("extract_sparse_subset", &extract_sparse_subset);
}
