from mattress import initialize
import delayedarray
import random
import numpy

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def simulate_SparseNdarray(nr, nc, dtype, itype):
    contents = []
    for i in range(nc):
        if random.random() < 0.5:
            contents.append(None)
            continue
        curdata = []
        curindex = []
        for r in range(nr):
            if random.random() < 0.2:
                curdata.append(random.random() * 100)
                curindex.append(r)
        contents.append((numpy.array(curindex, dtype=itype), numpy.array(curdata, dtype=dtype)))
    return delayedarray.SparseNdarray((nr, nc), contents, dtype, itype)


def test_SparseNdarray_data_type():
    for dt in [numpy.float64, numpy.float32, numpy.int64, numpy.int32, numpy.int16, numpy.int8, numpy.uint64, numpy.uint32, numpy.uint16, numpy.uint8]:
        m = simulate_SparseNdarray(100, 50, dt, numpy.int32)
        ptr = initialize(m)
        assert all(ptr.row(0) == m[0, :])
        assert all(ptr.column(1) == m[:, 1])


def test_SparseNdarray_index_type():
    for it in [numpy.int64, numpy.int32, numpy.int16, numpy.int8, numpy.uint64, numpy.uint32, numpy.uint16, numpy.uint8]:
        m = simulate_SparseNdarray(50, 100, numpy.float64, it)
        ptr = initialize(m)
        assert all(ptr.row(0) == m[0, :])
        assert all(ptr.column(1) == m[:, 1])


def test_SparseNdarray_empty():
    m = delayedarray.SparseNdarray((10, 2), [None, None], numpy.float64, numpy.int32)
    ptr = initialize(m)
    assert all(ptr.row(0) == m[0, :])
    assert all(ptr.column(1) == m[:, 1])

    m = delayedarray.SparseNdarray((10, 2), None, numpy.float64, numpy.int32)
    ptr = initialize(m)
    assert all(ptr.row(0) == m[0, :])
    assert all(ptr.column(1) == m[:, 1])
