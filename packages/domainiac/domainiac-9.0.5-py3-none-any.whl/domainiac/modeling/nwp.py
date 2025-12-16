from dataclasses import dataclass
from enum import Enum


class NWPParameter(Enum):
    SOLAR = "Solar"
    WIND = "Wind"
    TEMPERATURE = "Temperature"


class NWPProvider(Enum):
    ECMWF = "Ecmwf"
    CONWX = "Conwx"
    DMI = "Dmi"


@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float
    altitude: float


@dataclass(frozen=True)
class Neighborhood:
    coordinate: Coordinate
    num_neighbors: int
