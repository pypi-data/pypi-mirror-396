#include "pybind11/pybind11.h"

void init_common(pybind11::module&);
void init_dense_matrix(pybind11::module&);
void init_compressed_sparse_matrix(pybind11::module&);
void init_fragmented_sparse_matrix(pybind11::module&);
void init_delayed_binary_isometric_operation(pybind11::module&);
void init_delayed_bind(pybind11::module&);
void init_delayed_subset(pybind11::module&);
void init_delayed_transpose(pybind11::module&);
void init_delayed_unary_isometric_operation_simple(pybind11::module&);
void init_delayed_unary_isometric_operation_with_args(pybind11::module&);
void init_unknown_matrix(pybind11::module&);

PYBIND11_MODULE(lib_mattress, m) {
    init_common(m);
    init_dense_matrix(m);
    init_compressed_sparse_matrix(m);
    init_fragmented_sparse_matrix(m);
    init_delayed_binary_isometric_operation(m);
    init_delayed_bind(m);
    init_delayed_subset(m);
    init_delayed_transpose(m);
    init_delayed_unary_isometric_operation_simple(m);
    init_delayed_unary_isometric_operation_with_args(m);
    init_unknown_matrix(m);
}
