import datamazing.pandas as pdz
import pandas as pd
from typeguard import typechecked

from ..wrappers import cache_decorator

DEFAULT_RESOLUTION = pd.Timedelta("PT5M")


class ResourceManager:
    """
    Manager which simplifies the process of handling resource schedules.
    Scheduled resources are delivered in a 5 min resolution. If a higher
    resolution is chosen,
    the result will be the most conservative value in the time interval,
    e.i. max of minimum capacity and min of maximum capacity.
    If no resolution is given, the default is 5 min.
    If resolution is less than 5 min, the resulting time series will
    default to 5 min resolution.
    """

    def __init__(
        self,
        db: pdz.Database,
        time_interval: pdz.TimeInterval,
        resolution: pd.Timedelta = DEFAULT_RESOLUTION,
        cache_reource_schedules: bool = False,
    ) -> None:
        self.db = db
        self.time_interval = time_interval
        self.resolution = resolution
        self.cache_reource_schedules = cache_reource_schedules

    resource_schedules_cache = {}

    @typechecked
    def _query_resource_schedules(self, table: str) -> pd.DataFrame:
        return self.db.query(
            table_name=table,
            time_interval=self.time_interval,
        )

    @typechecked
    def query_resource_schedules(self, table: str) -> pd.DataFrame:
        if self.cache_reource_schedules:
            cached_query = cache_decorator(self.resource_schedules_cache)(
                self._query_resource_schedules
            )
            df = cached_query(table)
        else:
            df = self._query_resource_schedules(table)
        return df

    @typechecked
    def get_resource_schedules(self, resource_gsrn: str | list[str]) -> pd.DataFrame:
        """Gets resource schedules for a given list of resource gsrns."""
        df_resource_schedules = self.query_resource_schedules(
            "scheduleResourcePowerPlan"
        )

        if isinstance(resource_gsrn, str):
            resource_gsrn = [resource_gsrn]
        df_resource_schedules = df_resource_schedules[
            df_resource_schedules["resource_gsrn"].isin(resource_gsrn)
        ]

        if self.resolution != DEFAULT_RESOLUTION:
            df_resource_schedules = (
                pdz.group(
                    df_resource_schedules,
                    by=[
                        "market_participant",
                        "created_time_utc",
                        "price_area",
                        "resource_gsrn",
                    ],
                )
                .resample(on="time_utc", resolution=self.resolution)
                .agg(
                    {
                        "schedule_power_MW": "mean",
                        "schedule_capacity_min_MW": "max",
                        "schedule_capacity_max_MW": "min",
                    }
                )
                .dropna()
            )
        return df_resource_schedules.drop(
            columns=["masterdata_gsrn", "datahub_gsrn_e18"], errors="ignore"
        )

    @typechecked
    def get_latest_resource_schedules(
        self,
        resource_gsrn: str | list[str],
    ) -> pd.DataFrame:
        """Gets the lastest resource schedules for a given list of resource gsrns."""

        df_resource_schedules = self.get_resource_schedules(resource_gsrn=resource_gsrn)

        df_latest_created_time = pdz.group(
            df=df_resource_schedules, by=["resource_gsrn", "time_utc"]
        ).agg({"created_time_utc": "max"})

        df_resource_latest = df_latest_created_time.merge(
            df_resource_schedules, on=list(df_latest_created_time.columns)
        )

        return df_resource_latest
