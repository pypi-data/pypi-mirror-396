import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import interpolate

from domainiac.functions import conversions
from domainiac.functions.typing import RealFunction


def interpolate_wind_components(
    times: pd.Series, wind_components: pd.DataFrame
) -> RealFunction:
    """Interpolate wind vector using linear interpolation
    between observed values on the u- and v-components separately.

    Args:
        times (pd.Series): Times
        wind_components (pd.DataFrame): Observed values

    Returns:
        RealFunction: Interpolation function
    """
    x = conversions.datetime_to_float(times)
    y = conversions.as_array(wind_components)

    f = interpolate.make_interp_spline(x, y, k=1)

    bounds = (x.min(), x.max())

    def estimate(times: pd.Series) -> NDArray[np.float64]:
        x = conversions.datetime_to_float(times)
        y = f(x)
        y[(x < bounds[0]) | (x > bounds[1]), :] = np.nan
        return y

    return estimate
