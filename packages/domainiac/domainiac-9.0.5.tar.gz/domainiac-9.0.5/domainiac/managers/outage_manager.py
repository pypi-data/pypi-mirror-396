import datamazing.pandas as pdz
import pandas as pd


class OutageManager:
    """
    Manager which simplifies the process of getting outage data.
    """

    def __init__(
        self,
        db: pdz.Database,
        time_interval: pdz.TimeInterval,
        resolution: pd.Timedelta,
    ) -> None:
        self.db = db
        self.time_interval = time_interval
        self.resolution = resolution

    def get_plant_outage_time_series(self) -> pd.DataFrame:
        df_outage = self.db.query("scheduleOutage")

        df_outage = df_outage[~df_outage["is_unapproved"]]

        df_outage = df_outage.dropna(subset="plant_gsrn")

        # make placeholder dataframe to explode outage
        # data to all time points for all plants
        df_times = self.time_interval.to_range(self.resolution).to_frame(
            index=False, name="time_utc"
        )

        df_plants = df_outage[["plant_gsrn"]].drop_duplicates()

        df_idx = df_times.merge(df_plants, how="cross")

        df_outage = pdz.merge(
            df_idx,
            df_outage,
            on=["plant_gsrn"],
            left_time="time_utc",
            right_period=("start_time_utc", "end_time_utc"),
        )

        df_outage = df_outage.filter(
            [
                "plant_gsrn",
                "time_utc",
            ]
        )

        df_outage = df_outage.reset_index(drop=True)

        return df_outage
