from typing import Callable

import numpy as np
from numpy.typing import NDArray

IntegrableRealFunction = Callable[[NDArray[np.float64]], NDArray[np.float64]]

RealFunction = Callable[[NDArray[np.float64]], NDArray[np.float64]]
