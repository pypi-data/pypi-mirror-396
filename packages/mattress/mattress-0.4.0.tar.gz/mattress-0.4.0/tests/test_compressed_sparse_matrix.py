from mattress import initialize
import numpy
import scipy.sparse

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_sparse_csr_matrix_dtype():
    m0 = scipy.sparse.rand(100, 50, density=0.25, format="csr", random_state=42) * 100
    for dt in [numpy.float64, numpy.float32, numpy.int64, numpy.int32, numpy.int16, numpy.int8, numpy.uint64, numpy.uint32, numpy.uint16, numpy.uint8]:
        m = m0.astype(dt)
        assert isinstance(m, scipy.sparse.csr_matrix)
        ptr = initialize(m)
        assert all(ptr.row(0) == m[0, :].toarray()[0])
        assert all(ptr.column(1) == m[:, 1].toarray().flatten())


def test_sparse_csr_matrix_index_dtype():
    m0 = scipy.sparse.rand(100, 50, density=0.25, format="csr", random_state=69)
    for it in [numpy.int64, numpy.int32, numpy.int16, numpy.int8, numpy.uint32, numpy.uint16, numpy.uint8]: # scipy doesn't support uint64, apparently...
        m = m0.copy()
        m.indices = m.indices.astype(it)
        assert isinstance(m, scipy.sparse.csr_matrix)
        ptr = initialize(m)
        assert all(ptr.row(0) == m[0, :].toarray()[0])
        assert all(ptr.column(1) == m[:, 1].toarray().flatten())


def test_sparse_csr_array():
    m = scipy.sparse.rand(3, 4, density=0.25, format="csr", random_state=42).tocsr()
    ptr = initialize(m)
    assert all(ptr.row(0) == m[0, :].toarray()[0])
    assert all(ptr.column(1) == m[:, 1].toarray().flatten())


def test_sparse_csc_matrix():
    m = scipy.sparse.rand(3, 4, density=0.25, format="csc", random_state=42)
    ptr = initialize(m)
    assert all(ptr.row(0) == m[0, :].toarray()[0])
    assert all(ptr.column(1) == m[:, 1].toarray().flatten())


def test_sparse_csc_array():
    m = scipy.sparse.rand(3, 4, density=0.25, format="csc", random_state=42).tocsc()
    ptr = initialize(m)
    assert all(ptr.row(0) == m[0, :].toarray()[0])
    assert all(ptr.column(1) == m[:, 1].toarray().flatten())
