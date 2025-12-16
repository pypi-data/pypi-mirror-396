import datamazing.pandas as pdz
import pandas as pd
from typeguard import typechecked

from ..wrappers import cache_decorator


class MasterdataManager:
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

    masterdata_cache = {}

    @typechecked
    def _get_operational_entities(self, table: str) -> pd.DataFrame:
        filters = {"standing_entity_state": "InOperation"}
        df = self.db.query(table, filters=filters)
        df = df[df["decommission_date_utc"].isna()].reset_index(drop=True)
        return df

    @typechecked
    def get_operational_entities(self, table: str) -> pd.DataFrame:
        """Gets the operational data for a given table."""

        if self.cache_masterdata:
            cached_query = cache_decorator(self.masterdata_cache)(
                self._get_operational_entities
            )
            df = cached_query(table)
        else:
            df = self._get_operational_entities(table)

        return df

    @typechecked
    def get_data(
        self,
        table: str,
        filters: dict = {},
        columns: list = [],
    ) -> pd.DataFrame:
        """Gets the data for a given table.
        Filters for rows valid at the end of time interval.
        """
        # Get operational entities
        df = self.get_operational_entities(table)

        # Apply the filters
        for column, value in filters.items():
            if isinstance(value, list):
                df = df[df[column].isin(value)].reset_index()
            else:
                df = df[df[column] == value].reset_index()

        for column in columns:
            if column not in df.columns:
                raise KeyError(f"Column {column} not found in {table}")

        df = pdz.as_of_time(
            df=df,
            period=("valid_from_date_utc", "valid_to_date_utc"),
            at=self.time_interval.right,
        )
        df = df.filter(columns)

        return df
