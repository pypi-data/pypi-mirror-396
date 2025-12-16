import datamazing.pandas as pdz
import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree

from domainiac import functions

from ..modeling.nwp import Coordinate, Neighborhood, NWPParameter, NWPProvider


class NWPManager:
    """
    Contains all logic concerning NWP data.
    This includes:
    - Getting NWP data
    - Getting average NWP data
    - Finding closest NWP coordinates
    """

    def __init__(
        self,
        db: pdz.Database,
        time_interval: pdz.TimeInterval,
        resolution: pd.Timedelta,
    ):
        self.db = db
        self.time_interval = time_interval
        self.resolution = resolution

        self._nwp_coordinates_kd_tree = dict()
        self._nwp_table_name_prefix = "forecastNwp"

    @staticmethod
    def calculate_wind_speed_from_vectors(u: pd.Series, v: pd.Series) -> pd.Series:
        return np.sqrt(u**2 + v**2)

    def _get_table_name(
        self,
        provider: NWPProvider,
        parameter: NWPParameter,
    ) -> str:
        """
        Get the table name for a given NWP parameter.
        """
        return self._nwp_table_name_prefix + provider.value + parameter.value

    def _get_kd_tree(self, provider: NWPProvider, parameter: NWPParameter) -> KDTree:
        """
        Create a KDTree from the coordinates from the nwp parameter table.
        This is done lazily, so that the KDTree is only created once.
        """
        key = (provider, parameter)
        if key not in self._nwp_coordinates_kd_tree:
            # Base KDTree on six hours of data,
            # which should be enough to cover the largest interval which is ECMWF
            query_time_interval = pdz.TimeInterval(
                self.time_interval.left, self.time_interval.left + pd.Timedelta("PT6H")
            )

            df = self.db.query(
                table_name=self._get_table_name(provider, parameter),
                time_interval=query_time_interval,
            )

            self._nwp_coordinates_kd_tree[key] = dict()

            # Make KDTree for altitude
            self._nwp_coordinates_kd_tree[key]["altitude"] = KDTree(
                df[["altitude_m"]].drop_duplicates()
            )

            # Make KDTree for latitude and longitude
            self._nwp_coordinates_kd_tree[key]["plane"] = KDTree(
                df[["latitude", "longitude"]].drop_duplicates()
            )

        return self._nwp_coordinates_kd_tree[key]

    def get_nwp_neighbors(
        self,
        provider: NWPProvider,
        parameter: NWPParameter,
        neighborhood: Neighborhood,
    ) -> list[Coordinate]:
        """
        Find n closest coordinates based on the NWP parameter table.

        Note: This assumes that coordinates does not change over time.
        """
        kd_tree = self._get_kd_tree(provider, parameter)

        altitude_indices = kd_tree["altitude"].query(
            np.c_[neighborhood.coordinate.altitude],
            k=1,
            return_distance=False,
        )
        # TODO: Allow this to handle multiple altitudes
        nearest_altitude = kd_tree["altitude"].data.base[altitude_indices][0][0][0]

        plane_indices = kd_tree["plane"].query(
            np.c_[neighborhood.coordinate.latitude, neighborhood.coordinate.longitude],
            k=neighborhood.num_neighbors,
            return_distance=False,
        )
        nearest_planes = kd_tree["plane"].data.base[plane_indices][0]

        coordinates = [
            Coordinate(latitude=plane[0], longitude=plane[1], altitude=nearest_altitude)
            for plane in nearest_planes
        ]

        return coordinates

    def _get_nwp_parameter(
        self,
        provider: NWPProvider,
        parameter: NWPParameter,
        coordinate: Coordinate,
    ) -> pd.DataFrame:
        """
        Get NWP data for a given parameter, coordinate and altitude.
        """
        table = self._get_table_name(provider, parameter)

        filters = {
            "latitude": coordinate.latitude,
            "longitude": coordinate.longitude,
            "altitude_m": coordinate.altitude,
        }

        # Since we need to interpolate along the time dimension, we need to pad
        # the desired time interval when querying data, so we ensure we have data
        # points to interpolate between. Padding with 6 hours should be enough
        # for all our current NWP providers
        query_margin = pd.Timedelta("P6H")
        padded_time_interval = pdz.TimeInterval(
            self.time_interval.left - query_margin,
            self.time_interval.right + query_margin,
        )

        df = self.db.query(table, padded_time_interval, filters=filters)

        df = df.drop(
            columns=[
                "created_time_utc",
                "valid_from_time_utc",
                "valid_to_time_utc",
                "altitude_m",
                "longitude",
                "latitude",
            ],
            errors="ignore",
        )

        return df

    def _get_interpolated_nwp_parameter(
        self,
        provider: NWPProvider,
        parameter: NWPParameter,
        coordinate: Coordinate,
    ):
        """
        Get NWP data for a given parameter, coordinate and altitude,
        using the proper interpolation technique.
        """
        df = self._get_nwp_parameter(provider, parameter, coordinate)

        df = df.sort_values(by="time_utc")

        if parameter == NWPParameter.TEMPERATURE:
            column_names = "temperature_K"
            interpolated_function = functions.interpolate_temperature(
                times=df["time_utc"], temperature=df[column_names]
            )
        elif parameter == NWPParameter.SOLAR:
            column_names = "global_radiation_W_m2"
            interpolated_function = functions.interpolate_irradiance(
                coordinate=coordinate,
                times=df["time_utc"],
                radiation_avg=df[column_names].iloc[1:],
            )
        elif parameter == NWPParameter.WIND:
            column_names = ["wind_u_m_s", "wind_v_m_s"]
            interpolated_function = functions.interpolate_wind_components(
                times=df["time_utc"],
                wind_components=df[column_names],
            )

        df_interpolated = self.time_interval.to_range(freq=self.resolution).to_frame(
            name="time_utc"
        )

        df_interpolated[column_names] = interpolated_function(
            df_interpolated["time_utc"]
        )

        # remove nan values from the interpolated data
        # (for example when data has been extrapolated)
        df = df_interpolated.dropna(subset=column_names)

        # remove values outside the original time interval
        df_interpolated = df_interpolated[
            df_interpolated["time_utc"].between(
                df["time_utc"].min(), df["time_utc"].max()
            )
        ]

        return df_interpolated

    def get_nwp_parameter(
        self,
        provider: NWPProvider,
        parameter: NWPParameter,
        coordinate: Coordinate,
    ):
        df_nwp = self._get_interpolated_nwp_parameter(provider, parameter, coordinate)

        # Ensure data is within time_interval defined by user
        df_nwp = df_nwp.query(
            f"time_utc >= '{self.time_interval.left}' "
            f"and time_utc <= '{self.time_interval.right}'",
        )

        return df_nwp

    def get_nwp_parameter_in_neighborhood(
        self,
        provider: NWPProvider,
        parameter: NWPParameter,
        neighborhood: Neighborhood,
    ) -> pd.DataFrame:
        """
        Get average NWP data for a given parameter, coordinates and altitude.
        """
        dfs = []

        neighbors = self.get_nwp_neighbors(provider, parameter, neighborhood)
        for coordinate in neighbors:
            df_coordinate = self.get_nwp_parameter(provider, parameter, coordinate)
            dfs.append(df_coordinate)

        df = pd.concat(dfs)
        df = pdz.group(df, "time_utc").agg("mean")

        return df

    def get_nwp(
        self,
        provider: NWPProvider,
        parameters: list[NWPParameter],
        neighborhood: Neighborhood,
    ) -> pd.DataFrame:
        """
        Get weather features for a given coordinate.
        """
        dfs = []
        for parameter in parameters:
            df_param = self.get_nwp_parameter_in_neighborhood(
                provider,
                parameter,
                neighborhood,
            )
            dfs.append(df_param)

        df = pdz.merge_many(dfs=dfs, on=["time_utc"])

        return df
