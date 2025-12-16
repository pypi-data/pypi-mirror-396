import numpy as np

ORIGIN = np.datetime64("2020-01-01")
UNIT = np.timedelta64(1, "s")


def as_array(values):
    return np.array(values)


def timedelta_to_float(values):
    return as_array(values).astype("timedelta64") / UNIT


def float_to_timedelta(values):
    return as_array(values) * UNIT


def datetime_to_float(values):
    return timedelta_to_float(as_array(values).astype("datetime64") - ORIGIN)


def float_to_datetime(values):
    return float_to_timedelta(values) + ORIGIN
