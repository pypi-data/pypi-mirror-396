import numpy
import delayedarray
import mattress
import pytest


class SomethingUnknown:
    def __init__(self, core):
        self._core = core

    @property
    def shape(self):
        return self._core.shape

    def __getitem__(self, *args, **kwargs):
        return self._core.__getitem__(*args, **kwargs)


@delayedarray.is_sparse.register
def is_sparse_unknown(x: SomethingUnknown):
    return delayedarray.is_sparse(x._core)


@delayedarray.chunk_grid.register
def chunk_grid_unknown(x: SomethingUnknown):
    return delayedarray.chunk_grid(x._core)


@delayedarray.extract_dense_array.register
def extract_dense_array(x: SomethingUnknown, indices):
    return delayedarray.extract_dense_array(x._core, indices)


@delayedarray.extract_sparse_array.register
def extract_sparse_array(x: SomethingUnknown, indices):
    return delayedarray.extract_sparse_array(x._core, indices)


def test_unknown_matrix(capsys):
    y = SomethingUnknown(numpy.random.rand(1000, 100) * 100)

    ptr = mattress.initialize(y)
    captured = capsys.readouterr()
    assert "unknown matrix fallback" in captured.out

    assert all(ptr.row(0) == y[0, :])
    assert all(ptr.column(1) == y[:, 1])
    assert ptr.shape == (1000, 100)

    with pytest.warns(UserWarning, match="unknown matrix fallback"):
        ptr = mattress.initialize(y, _unknown_action="warn")
    with pytest.raises(NotImplementedError, match="not supported"):
        ptr = mattress.initialize(y, _unknown_action="error")


def test_unknown_operation(capsys):
    y = delayedarray.DelayedArray(numpy.random.rand(1000, 100))
    y = numpy.round(y, decimals=2)

    ptr = mattress.initialize(y)
    captured = capsys.readouterr()
    assert "unknown matrix fallback" in captured.out

    assert all(ptr.row(0) == y[0, :])
    assert all(ptr.column(1) == y[:, 1])
    assert ptr.shape == (1000, 100)

    with pytest.warns(UserWarning, match="unknown matrix fallback"):
        ptr = mattress.initialize(y, _unknown_action="warn")
    with pytest.raises(NotImplementedError, match="not yet supported"):
        ptr = mattress.initialize(y, _unknown_action="error")
