import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import interpolate

from domainiac.functions import conversions
from domainiac.functions.typing import RealFunction


def interpolate_temperature(times: pd.Series, temperature: pd.Series) -> RealFunction:
    """Interpolate temperature using linear interpolation between
    observed values.

    Args:
        times (pd.Series): Times of observations
        temperature (pd.Series): Observed values

    Returns:
        RealFunction: Interpolation function
    """
    x = conversions.datetime_to_float(times)
    y = conversions.as_array(temperature)

    f = interpolate.make_interp_spline(x, y, k=1)

    bounds = (x.min(), x.max())

    def estimate(times: pd.Series) -> NDArray[np.float64]:
        x = conversions.datetime_to_float(times)
        y = f(x)
        y[(x < bounds[0]) | (x > bounds[1])] = np.nan
        return y

    return estimate
