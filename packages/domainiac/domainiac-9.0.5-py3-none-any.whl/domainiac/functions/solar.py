import numpy as np
import pandas as pd
import pvlib
from numpy.typing import NDArray

from domainiac.functions import conversions, interpolation
from domainiac.modeling import Coordinate


def clearsky_irradiance(
    times: NDArray[np.datetime64], coordinate: Coordinate
) -> NDArray[np.float64]:
    """Get the clearsky irradiance (W/m2) for a specific coordinate

    Args:
        times (NDArray[np.datetime64]): Times
        coordinate (Coordinate): Coordinate
    """

    location = pvlib.location.Location(coordinate.latitude, coordinate.longitude)

    # ensure 1D-array both when input is
    # scalar and 1D-array already
    array = conversions.as_array([times])
    if array.size != 1:
        array = array.squeeze()

    times = pd.DatetimeIndex(array)
    # pvlibs `get_clearsky` will return 0
    # if datetime unit is anything else than
    # nanoseconds (probably due to some
    # internal conversion going wrong)
    times = times.as_unit("ns")

    clearsky = location.get_clearsky(times)

    return clearsky["ghi"].to_numpy()


def interpolate_irradiance(
    coordinate: Coordinate, times: pd.Series, radiation_avg: pd.Series
):
    """Interpolate solar irradiance (i.e. instantaneous values) using
    binned index interpolation (using the clearsky irradiance as the reference profile)
    between observed values of solar radiance (i.e. binned average values)

    Args:
        coordinate (Coordinate): Coordinate
        times (pd.Series): Sequence of times defining the intervals of observations
        radiation (pd.Series): Observed values of radiation
    """

    def profile(x: NDArray[np.float64]) -> NDArray[np.float64]:
        times = conversions.float_to_datetime(x)
        return clearsky_irradiance(times, coordinate)

    x = conversions.datetime_to_float(times)
    y_avg = conversions.as_array(radiation_avg)
    # 5-minute step size should be sufficient for evaluating the clearsky integral
    quad_step_size = conversions.timedelta_to_float(pd.Timedelta("PT5M"))

    f = interpolation.binned_index_interpolation(profile, x, y_avg, quad_step_size)

    def estimate(times: pd.Series) -> NDArray[np.float64]:
        x = conversions.datetime_to_float(times)
        return f(x)

    return estimate
