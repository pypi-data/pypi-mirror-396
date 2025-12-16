import numpy as np
import delayedarray as da
from mattress import initialize

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_delayed_unary_isometric_log():
    y = np.random.rand(1000, 100)
    x = da.DelayedArray(y)

    z = np.log1p(x)
    assert isinstance(z.seed, da.UnaryIsometricOpSimple)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.log1p(y[0, :]))
    assert np.allclose(ptr.column(1), np.log1p(y[:, 1]))

    z = np.log2(x)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.log2(y[0, :]))
    assert np.allclose(ptr.column(1), np.log2(y[:, 1]))

    z = np.log10(x)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.log10(y[0, :]))
    assert np.allclose(ptr.column(1), np.log10(y[:, 1]))

    z = np.log(x)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.log(y[0, :]))
    assert np.allclose(ptr.column(1), np.log(y[:, 1]))


def test_delayed_unary_isometric_sign():
    y = np.random.rand(1000, 100) - 0.5
    x = da.DelayedArray(y)

    z = np.sign(x)
    assert isinstance(z.seed, da.UnaryIsometricOpSimple)
    ptr = initialize(z)
    assert all(ptr.row(0) == np.sign(y[0, :]))
    assert all(ptr.column(1) == np.sign(y[:, 1]))

    z = np.abs(x)
    ptr = initialize(z)
    assert all(ptr.row(0) == np.abs(y[0, :]))
    assert all(ptr.column(1) == np.abs(y[:, 1]))


def test_delayed_unary_isometric_sqrt():
    y = np.random.rand(1000, 100)
    x = da.DelayedArray(y)

    z = np.sqrt(x)
    assert isinstance(z.seed, da.UnaryIsometricOpSimple)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.sqrt(y[0, :]))
    assert np.allclose(ptr.column(1), np.sqrt(y[:, 1]))


def test_delayed_unary_isometric_int():
    y = np.random.rand(1000, 100) * 10
    x = da.DelayedArray(y)

    z = np.ceil(x)
    assert isinstance(z.seed, da.UnaryIsometricOpSimple)
    ptr = initialize(z)
    assert all(ptr.row(0) == np.ceil(y[0, :]))
    assert all(ptr.column(1) == np.ceil(y[:, 1]))

    z = np.floor(x)
    ptr = initialize(z)
    assert all(ptr.row(0) == np.floor(y[0, :]))
    assert all(ptr.column(1) == np.floor(y[:, 1]))

    z = np.trunc(x)
    ptr = initialize(z)
    assert all(ptr.row(0) == np.trunc(y[0, :]))
    assert all(ptr.column(1) == np.trunc(y[:, 1]))

    z = np.round(x)
    ptr = initialize(z)
    assert all(ptr.row(0) == np.round(y[0, :]))
    assert all(ptr.column(1) == np.round(y[:, 1]))


def test_delayed_unary_isometric_exp():
    y = np.random.rand(1000, 100)
    x = da.DelayedArray(y)

    z = np.exp(x)
    assert isinstance(z.seed, da.UnaryIsometricOpSimple)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.exp(y[0, :]))
    assert np.allclose(ptr.column(1), np.exp(y[:, 1]))

    z = np.expm1(x)
    ptr = initialize(z)
    assert np.allclose(ptr.row(0), np.expm1(y[0, :]))
    assert np.allclose(ptr.column(1), np.expm1(y[:, 1]))


def test_delayed_unary_isometric_trig():
    y = np.random.rand(1000, 100)
    x = da.DelayedArray(y)

    for op in [
        "cos",
        "sin",
        "tan",
        "cosh",
        "sinh",
        "tanh",
        "arccos",
        "arcsin",
        "arctan",
        "arctanh",
    ]:
        fun = getattr(np, op)
        z = fun(x)
        assert isinstance(z.seed, da.UnaryIsometricOpSimple)
        ptr = initialize(z)
        assert np.allclose(ptr.row(0), fun(y[0, :]))
        assert np.allclose(ptr.column(1), fun(y[:, 1]))

    y = y + 1
    x = da.DelayedArray(y)
    for op in ["arccosh", "arcsinh"]:
        fun = getattr(np, op)
        z = fun(x)
        assert isinstance(z.seed, da.UnaryIsometricOpSimple)
        ptr = initialize(z)
        assert np.allclose(ptr.row(0), fun(y[0, :]))
        assert np.allclose(ptr.column(1), fun(y[:, 1]))
