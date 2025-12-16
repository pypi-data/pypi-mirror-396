import numpy as np
from numpy.typing import NDArray
from scipy import integrate, interpolate

from domainiac.functions.typing import IntegrableRealFunction


def cumulative_integral(
    f: IntegrableRealFunction,
    x: NDArray[np.float64],
    step_size: np.float64,
) -> NDArray[np.float64]:
    """Given an integrable real function f : R -> R,
    calculate the cumulative integral values

        int_{x0}^{x}f(s)ds

    The calculation is numerical, using the trapezoid
    rule with the specified step size.

    Args:
        f (IntegrableUnivariate): Function
        x (NDArray[np.float64]): Points to evaluate at.
        step_size (np.float64): Step size used in the quadrature.

    Returns:
        NDArray[np.float64]: Values of the cumulative integral
            at the specified points
    """
    xi = np.arange(start=x[0], stop=x[-1] + step_size, step=step_size)
    yi = f(xi)

    Yi = integrate.cumulative_trapezoid(yi, xi, initial=0)

    Y = Yi[np.searchsorted(xi, x)]

    return Y


def midpoint(x: NDArray) -> NDArray:
    """Calculate the midpoints of intervals
    giving a sequence of points.

    Args:
        x (NDArray): Sequence of points defining the intervals (size N)

    Returns:
        NDArray: Midpoints of intervals (size N-1)
    """
    return x[:-1] + 0.5 * np.diff(x)


def binned_index_interpolation(
    profile: IntegrableRealFunction,
    x: NDArray[np.float64],
    y_avg: NDArray[np.float64],
    quad_step_size: float,
) -> IntegrableRealFunction:
    """
    Compute binned index interpolation function. The setup here is as follows:
    Suppose you have an unknown function f, but which is known to have the
    form f=i*profile, where i is an function taking values between 0 and 1.
    Given is only the average value of f on a sequence of intervals.

    This method calculates the ratios

        (integral of f on interval i)/(integral of profile on interval i)

    i is then estimated by doing spline interpolation between these ratios.

    Note:
        This method does NOT ensure that the average values are preserved.
        To accomplish this, a different method is required, but is has been
        decided to not go further into this topic, as the preliminary results
        seem promising enough.

    Args:
        profile (IntegrableRealFunction): Profile function
        x (NDArray[np.float64]): Sequence of points defining the intervals (size N)
        y_avg (NDArray[np.float64]): Average value on the intervals (size N-1)
        --- additional settings for solver ---
        quad_step_size (float): Step size used in quadrature of profile function.

    Returns:
        IntegrableRealFunction: Estimated base function.
    """
    x = np.array(x)
    y_avg = np.array(y_avg)

    Yp = cumulative_integral(profile, x, step_size=quad_step_size)

    yp_avg = (Yp[1:] - Yp[:-1]) / (x[1:] - x[:-1])

    bin_index = y_avg / yp_avg

    bin_midpoints = midpoint(x)

    # if the index is invalid (due to the profile being zero)
    # we set the index to 1. Since the profile is zero in this
    # case, it will not matter to the final function (though
    # it might have an impact on the values surrounding these
    # point)
    is_valid = ~np.isnan(bin_index) & ~np.isinf(bin_index)

    bin_index[~is_valid] = 1

    # the index might be outside the expected range
    # due to errors in the input data. In this case
    # we clip it
    bin_index = np.clip(bin_index, a_min=0, a_max=1)

    index = interpolate.PchipInterpolator(
        x=bin_midpoints,
        y=bin_index,
        extrapolate=False,
    )

    def estimate(x: NDArray[np.float64]) -> NDArray[np.float64]:
        return index(x) * profile(x)

    return estimate
