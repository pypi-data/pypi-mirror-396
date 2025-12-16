import datamazing.pandas as pdz
import pandas as pd

from .masterdata_manager import MasterdataManager


class UnitManager(MasterdataManager):
    """
    Manager which simplifies the process of getting units from masterdata.
    """

    def __init__(
        self,
        db: pdz.Database,
        time_interval: pdz.TimeInterval,
        resolution: pd.Timedelta,
        cache_masterdata: bool = False,
    ) -> None:
        self.db = db
        self.time_interval = time_interval
        self.resolution = resolution
        self.cache_masterdata = cache_masterdata

    def get_units(
        self,
        filters: dict = {},
        columns: list | None = None,
    ) -> pd.DataFrame:
        """Gets the units for a given unit type.
        Filters for units valid at the end of time interval.
        Filters by default for units in operation.
        """
        default_columns = [
            "masterdata_gsrn",
            "plant_id",
            "power_system_resource_type",
        ]
        if not columns:
            columns = default_columns
        else:
            columns = list(set(default_columns + columns))
        return self.get_data("masterdataUnit", filters=filters, columns=columns)
