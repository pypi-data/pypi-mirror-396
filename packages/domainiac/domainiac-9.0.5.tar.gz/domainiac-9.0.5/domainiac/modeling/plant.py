from dataclasses import dataclass

import pandas as pd

from .nwp import Coordinate


@dataclass(frozen=True)
class Plant:
    plant_gsrn: str
    plant_name: str
    datahub_gsrn_e18: str
    price_area: str
    coordinate: Coordinate
    installed_power_MW: float
    power_system_resource_type: str

    @classmethod
    def plants_from_df(cls, df: pd.DataFrame) -> list["Plant"]:
        plants = []

        for _, row in df.iterrows():
            if "altitude" in row.keys():
                altitude = row["altitude"]
            else:
                altitude = 0

            if "power_system_resource_type" in row.keys():
                psrt = row["power_system_resource_type"]
            else:
                psrt = None

            plant = cls(
                plant_gsrn=row["plant_gsrn"],
                plant_name=row["plant_name"],
                datahub_gsrn_e18=row["datahub_gsrn_e18"],
                price_area=row["price_area"],
                coordinate=Coordinate(
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    altitude=altitude,
                ),
                installed_power_MW=row["installed_power_MW"],
                power_system_resource_type=psrt,
            )
            plants.append(plant)
        return plants


@dataclass(frozen=True)
class Group:
    coordinate: Coordinate
    installed_power_MW: float
    identifiers: dict[str, str]

    @classmethod
    def groups_from_df(cls, df: pd.DataFrame, identifiers: list[str]) -> list["Group"]:
        groups = []
        for _, row in df.iterrows():
            if "altitude" in row.keys():
                altitude = row["altitude"]
            else:
                altitude = 0

            identifiers = {identifier: row[identifier] for identifier in identifiers}
            group = cls(
                identifiers=identifiers,
                installed_power_MW=row["installed_power_MW"],
                coordinate=Coordinate(
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    altitude=altitude,
                ),
            )
            groups.append(group)
        return groups
