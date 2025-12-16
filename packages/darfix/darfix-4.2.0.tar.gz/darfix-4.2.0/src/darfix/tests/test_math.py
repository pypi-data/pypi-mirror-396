import numpy

from darfix.math import bivariate_gaussian
from darfix.math import compute_com_fwhm
from darfix.math import gaussian
from darfix.math import trivariate_gaussian


def test_gaussian():
    X = numpy.random.random((100))
    X0 = X.mean()

    result = gaussian(X, amplitude=1, x0=X0, fwhm=0.5, background=0)

    assert result.shape == (100,)


def test_bivariate_gaussian():
    X = numpy.random.random((2, 100))
    X0 = X.mean(axis=1)

    result = bivariate_gaussian(X, X0[0], X0[1], 0.5, 0.5, 1, 0.1)

    assert result.shape == (100,)


def test_trivariate_gaussian():
    X = numpy.random.random((3, 100))
    X0 = X.mean(axis=1)

    result = trivariate_gaussian(
        X,
        X0[0],
        X0[1],
        X0[2],
        fwhm_x0=1,
        fwhm_x1=1,
        fwhm_x2=1,
        c10=0.5,
        c20=0.2,
        c12=0.1,
        amplitude=1,
    )

    assert result.shape == (100,)


def test_compute_com_fwhm_1d():
    mean = [1.2]
    fwhm = [0.8]
    X = numpy.array([numpy.linspace(0, 3, 200)])
    Y = gaussian(X, 100, mean[0], fwhm[0], 0)

    numpy.testing.assert_array_almost_equal(
        [mean, fwhm], compute_com_fwhm(X, Y), decimal=2
    )


def test_compute_com_fwhm_2d():
    mean = [1.2, 4.3]
    fwhm = [0.5, 0.8]
    X = numpy.stack(
        numpy.meshgrid(numpy.linspace(0.2, 2, 22), numpy.linspace(3, 6, 30))
    ).reshape(2, -1)
    Y = bivariate_gaussian(X, mean[0], mean[1], fwhm[0], fwhm[1], 10)

    numpy.testing.assert_array_almost_equal(
        [mean, fwhm], compute_com_fwhm(X, Y), decimal=2
    )


def test_compute_com_fwhm_3d():
    mean = [1.2, 4.3, 3.0]
    fwhm = [0.5, 0.8, 0.1]
    X = numpy.stack(
        numpy.meshgrid(
            numpy.linspace(0.5, 2, 22),
            numpy.linspace(3, 5.5, 30),
            numpy.linspace(2.5, 3.5, 20),
        )
    ).reshape(3, -1)
    Y = trivariate_gaussian(
        X, mean[0], mean[1], mean[2], fwhm[0], fwhm[1], fwhm[2], 0, 0, 0, 10
    )

    numpy.testing.assert_array_almost_equal(
        [mean, fwhm], compute_com_fwhm(X, Y), decimal=2
    )
