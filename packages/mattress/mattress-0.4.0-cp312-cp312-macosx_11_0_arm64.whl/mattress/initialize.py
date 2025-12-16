from functools import singledispatch
from typing import Any, Literal

import numpy
import delayedarray
from biocutils.package_utils import is_package_installed

from .InitializedMatrix import InitializedMatrix
from . import lib_mattress as lib
from ._utils import _sanitize_subset, _contiguify

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


@singledispatch
def initialize(
    x: Any,
    _unknown_action: Literal["none", "message", "warn", "error"] = "message",
    **kwargs
) -> InitializedMatrix:
    """Initialize an :py:class:`~mattress.InitializedMatrix.InitializedMatrix`
    from a Python matrix representation. This prepares the matrix for use in
    C++ code that can accept a ``tatami::Matrix`` instance.

    Args:
        x:
            Any matrix-like object.

        _unknown_action:
            Action to take upon encountering an unknown matrix.
            If not ``error``, falls back to the unknown matrix handler with a message or warning.
            Otherwise, raises an error.

        kwargs:
            Additional named arguments for individual methods.

    Raises:
        NotImplementedError: if x is not supported.

    Returns:
        A pointer to tatami object.
    """
    if _unknown_action == "error":
        raise NotImplementedError(f"'initialize' is not supported for {type(x)} objects")

    if _unknown_action != "none":
        msg = f"using the unknown matrix fallback for {type(x)}"
        if _unknown_action == "message":
            print(msg)
        else:
            import warnings
            warnings.warn(msg, category=UserWarning)

    buffer_size = delayedarray.default_buffer_size()
    return InitializedMatrix(lib.initialize_unknown_matrix(x, int(buffer_size)))


@initialize.register
def _initialize_pointer(x: InitializedMatrix, **kwargs) -> InitializedMatrix:
    return x  # no-op


@initialize.register
def _initialize_numpy(x: numpy.ndarray, **kwargs) -> InitializedMatrix:
    if len(x.shape) != 2:
        raise ValueError("'x' should be a 2-dimensional array")
    x = _contiguify(x)
    return InitializedMatrix(lib.initialize_dense_matrix(x.shape[0], x.shape[1], x))


if is_package_installed("scipy"):
    import scipy.sparse


    @initialize.register
    def _initialize_sparse_csr_array(x: scipy.sparse.csr_array, **kwargs) -> InitializedMatrix:
        dtmp = _contiguify(x.data)
        itmp = _contiguify(x.indices)
        indtmp = x.indptr.astype(numpy.uint64, copy=False, order="A")
        return InitializedMatrix(lib.initialize_compressed_sparse_matrix(x.shape[0], x.shape[1], dtmp, itmp, indtmp, True))


    @initialize.register
    def _initialize_sparse_csr_matrix(x: scipy.sparse.csr_matrix, **kwargs) -> InitializedMatrix:
        return _initialize_sparse_csr_array(x)


    @initialize.register
    def _initialize_sparse_csc_array(x: scipy.sparse.csc_array, **kwargs) -> InitializedMatrix:
        dtmp = _contiguify(x.data)
        itmp = _contiguify(x.indices)
        indtmp = x.indptr.astype(numpy.uint64, copy=False, order="A")
        return InitializedMatrix(lib.initialize_compressed_sparse_matrix(x.shape[0], x.shape[1], dtmp, itmp, indtmp, False))


    @initialize.register
    def _initialize_sparse_csc_matrix(x: scipy.sparse.csc_matrix) -> InitializedMatrix:
        return _initialize_sparse_csc_array(x)


@initialize.register
def _initialize_delayed_array(x: delayedarray.DelayedArray, _unknown_action="message", **kwargs) -> InitializedMatrix:
    try:
        return initialize(x.seed, _unknown_action=_unknown_action, **kwargs)
    except Exception as e:
        if _unknown_action == "error":
            raise NotImplementedError(e)

        if _unknown_action != "none":
            msg = f"{str(e)}, using the unknown matrix fallback for {type(x)}"
            if _unknown_action == "message":
                print(msg)
            else:
                import warnings
                warnings.warn(msg, category=UserWarning)

        buffer_size = delayedarray.default_buffer_size()
        return InitializedMatrix(lib.initialize_unknown_matrix(x, int(buffer_size)))


@initialize.register
def _initialize_SparseNdarray(x: delayedarray.SparseNdarray, **kwargs) -> InitializedMatrix:
    if x.contents is not None:
        dvecs = []
        ivecs = []
        for y in x.contents:
            if y is None:
                ivecs.append(None)
                dvecs.append(None)
            else:
                ivecs.append(_contiguify(y[0]))
                dvecs.append(_contiguify(y[1]))
    else:
        nc = x.shape[1]
        dvecs = [None] * nc
        ivecs = [None] * nc

    return InitializedMatrix(lib.initialize_fragmented_sparse_matrix(x.shape[0], x.shape[1], dvecs, ivecs, False, x.dtype, x.index_dtype))


@initialize.register
def _initialize_delayed_unary_isometric_operation_simple(x: delayedarray.UnaryIsometricOpSimple, **kwargs) -> InitializedMatrix:
    components = initialize(x.seed, **kwargs)
    ptr = lib.initialize_delayed_unary_isometric_operation_simple(components.ptr, x.operation)
    return InitializedMatrix(ptr)


@initialize.register
def _initialize_delayed_unary_isometric_operation_with_args(x: delayedarray.UnaryIsometricOpWithArgs, **kwargs) -> InitializedMatrix:
    components = initialize(x.seed, **kwargs)

    if isinstance(x.value, numpy.ndarray):
        contents = x.value.astype(numpy.float64, copy=False, order="A")
        ptr = lib.initialize_delayed_unary_isometric_operation_with_vector(components.ptr, x.operation, x.right, (x.along == 0), contents)
    else:
        ptr = lib.initialize_delayed_unary_isometric_operation_with_scalar(components.ptr, x.operation, x.right, x.value)

    return InitializedMatrix(ptr)


@initialize.register
def _initialize_delayed_subset(x: delayedarray.Subset, **kwargs) -> InitializedMatrix:
    components = initialize(x.seed, **kwargs)
    for dim in range(2):
        current = x.subset[dim]
        noop, current = _sanitize_subset(current, x.shape[dim])
        if not noop:
            ptr = lib.initialize_delayed_subset(components.ptr, current, dim == 0)
            components = InitializedMatrix(ptr)
    return components


@initialize.register
def _initialize_delayed_bind(x: delayedarray.Combine, **kwargs) -> InitializedMatrix:
    collected = [initialize(s, **kwargs) for s in x.seeds]
    return InitializedMatrix(lib.initialize_delayed_bind([s.ptr for s in collected], x.along))


@initialize.register
def _initialize_delayed_transpose(x: delayedarray.Transpose, **kwargs) -> InitializedMatrix:
    components = initialize(x.seed, **kwargs)
    if x.perm == (1, 0):
        ptr = lib.initialize_delayed_transpose(components.ptr)
        components = InitializedMatrix(ptr)
    return components


@initialize.register
def _initialize_delayed_binary_isometric_operation(x: delayedarray.BinaryIsometricOp, **kwargs) -> InitializedMatrix:
    lcomponents = initialize(x.left, **kwargs)
    rcomponents = initialize(x.right, **kwargs)
    ptr = lib.initialize_delayed_binary_isometric_operation(lcomponents.ptr, rcomponents.ptr, x.operation)
    return InitializedMatrix(ptr)


@initialize.register
def _initialize_delayed_round(x: delayedarray.Round, **kwargs) -> InitializedMatrix:
    components = initialize(x.seed, **kwargs)
    if x.decimals != 0:
        raise NotImplementedError("non-zero decimals in 'delayedarray.Round' are not yet supported")
    ptr = lib.initialize_delayed_unary_isometric_operation_simple(components.ptr, "round")
    return InitializedMatrix(ptr)
