import datamazing.pandas as pdz
import pandas as pd
from typeguard import typechecked


class MeteringManager:
    """
    Manager which simplifies the process of getting metering data from datahub.
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

    @typechecked
    def get_plant_settlement(self, datahub_gsrn: str) -> pd.DataFrame:
        """
        Retrieves the settlement data for a given datahub gsrn.
        """
        df = self.db.query(
            "readingSettlement",
            self.time_interval,
            filters={"datahub_gsrn_e18": datahub_gsrn},
        )

        df = df.filter(
            [
                "time_utc",
                "datahub_gsrn_e18",
                "reading_settlement_e18_MW",
            ]
        )

        # Settlement data is an aggregated production in the interval [t, t+1],
        # therefore there is a timeshift of half the resolution. The data is
        # then interpolated to a production at hourly timestamps XX:00

        df = pdz.shift_time(df, on="time_utc", period=pd.Timedelta(minutes=30))
        df = pdz.resample(
            df, on="time_utc", resolution=pd.Timedelta(minutes=30)
        ).interpolate()
        # Because of interpolation, the GSRN for the new points is NAN,
        # they have to be backfilled with proper values
        df["datahub_gsrn_e18"] = datahub_gsrn

        df = df.drop(df[df["time_utc"].dt.minute != 0].index)
        df = df.reset_index().drop("index", axis=1)

        return df
