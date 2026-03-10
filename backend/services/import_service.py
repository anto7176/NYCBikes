#
#   Imports
#

import io
import pandas as pd # type: ignore
import geopandas as gpd # type: ignore

from datetime import datetime
from typing import Any, List
from pymongo import AsyncMongoClient
from fastapi.datastructures import UploadFile
from pymongo.errors import BulkWriteError
from shapely.geometry import LineString, mapping

# Perso

from enums.import_types import ImportType
from config.config import get_settings

#
#   Constants
#

BATCH_SIZE = 10000
BIKES_ITINERARY_DIVIDER_RATIO = 30
MATCHING_ACCIDENTS_RADIUS = 100
MAX_NB_MONTH_PER_IMPORT = 3

#
#   Services
#

settings = get_settings()

class ImportService:
    """
        Service to import collections to the database.
    """

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db[settings.DB_NAME]

    async def import_collection(self, import_type: ImportType, file: UploadFile) -> tuple[datetime, datetime]:
        """
            Import a collection from a CSV file.

            Params:
                - import_type: The type of the import.
                - file: The file to import.

            Returns:
                - start_date: The start date of the collection.
                - end_date: The end date of the collection.
        """

        # Reading the file
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        if df.empty:
            raise ValueError("No data found in the file !")
        await file.close()

        # Importing the collection
        if import_type == ImportType.ACCIDENTS:
            return await self.import_accidents(df)
        elif import_type == ImportType.BIKES_ITINERARY:
            return await self.import_bikes_itinerary(df)

    async def import_accidents(self, df: pd.DataFrame) -> tuple[datetime, datetime]:
        """
            Import accidents from a pandas DataFrame.

            Params:
                - df: The pandas DataFrame to import.

            Returns:
                - start_date: The start date of the accidents.
                - end_date: The end date of the accidents.

            Raises:
                - ValueError: If the number of months to import is greater than {MAX_NB_MONTH_PER_IMPORT} !
        """

        df = self._clean_accidents(df)

        #
        #   Processing the DataFrame
        #

        # Validating the number of months to import
        start_date, end_date = self._validate_monthly_period(df)

        # Transforming the accidents DataFrame to a GeoDataFrame
        gdf = self._transform_acc_to_gdf(df)

        # Converting the gdf to a MongoDDB compatible
        # coordinates system

        gdf["position"] = gdf["geometry"].apply(mapping) # type: ignore

        gdf.drop(columns=["geometry"], inplace=True) # type: ignore

        # Inserting the new accidents into the database
        await self._batch_insert(gdf, "accidents")

        return start_date, end_date

    async def import_bikes_itinerary(self, df: pd.DataFrame) -> tuple[datetime, datetime]:
        """
            Import bikes itinerary from a pandas DataFrame.

            Params:
                - df: The pandas DataFrame to import.

            Returns:
                - start_date: The start date of the bikes itinerary.
                - end_date: The end date of the bikes itinerary.

            Raises:
                - ValueError: If the number of months to import
                is greater than {MAX_NB_MONTH_PER_IMPORT} !
        """

        df = self._clean_bikes_itinerary(df)

        #
        #   Processing the DataFrame
        #

        # Validating the number of months to import
        start_date, end_date = self._validate_monthly_period(df)
        
        gdf = self._transform_bi_to_gdf(df)

        gdf["buffer"] = gdf["geometry"].apply(mapping) # type: ignore

        gdf.drop(columns=["geometry"], inplace=True) # type: ignore

        # Inserting the new bikes itinerary into the database
        await self._batch_insert(gdf, "bikes_itinerary")

        return start_date, end_date

    async def _batch_insert(
        self,
        df: pd.DataFrame,
        coll_name: str
    ) -> None:
        """
            Batch inserts the rows in the database.

            It ignores the duplicates that will be rejected by the db
            since it it has indexes on couple of columns.

            Params:
                - df: The df to insert
                - coll_name : The name of the collection to insert in.
        """
        
        df_dict = df.to_dict(orient="records") # type: ignore

        batch: List[Any] = []
        for i in range(len(df)):
            batch.append(df_dict[i])

            if len(batch) >= BATCH_SIZE or i >= len(df) - 1:
                try:
                    await self._db[coll_name].insert_many(
                        batch,
                        ordered=False
                    )
                except BulkWriteError:
                    pass

                batch = []
            
    def _clean_bikes_itinerary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
            Cleaning the bikes itinerary DataFrame.
        """

        # Removing useless columns
        df.drop(columns=[  # type: ignore
            "start_station_id",
            "end_station_id",
        ], inplace=True)

        # Renaming the column ride_id to _id
        df.rename(columns={"ride_id": "_id"}, inplace=True)
        
        # Dropping the rows with missing MAIN values
        df.dropna(subset=[
            "started_at",
            "ended_at",
            "start_lat",
            "start_lng",
            "end_lat",
            "end_lng",
        ], inplace=True)

        # Fixing the datetime columns
        df["started_at"] = pd.to_datetime( # type: ignore
            df["started_at"], # type: ignore
            format="%Y-%m-%d %H:%M:%S.%f"
        )
        df["ended_at"] = pd.to_datetime( # type: ignore
            df["ended_at"], # type: ignore
            format="%Y-%m-%d %H:%M:%S.%f"
        )

        df.infer_objects()

        # Fixing index
        df.reset_index(drop=True, inplace=True)

        # Keeping only some random rows to limit the size of the dataset
        df = df.sample(n=len(df) // BIKES_ITINERARY_DIVIDER_RATIO, random_state=42) # type: ignore

        return df

    def _transform_acc_to_gdf(
        self,
        df_acc: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """
            Transforming the accidents DataFrame into a GeoDataFrame.
        """

        gdf_acc = gpd.GeoDataFrame(
            df_acc,
            geometry=gpd.points_from_xy(
                df_acc["LONGITUDE"], # type: ignore
                df_acc["LATITUDE"], # type: ignore
            ),
            crs="EPSG:4326"
        )

        return gdf_acc
    
    def _transform_bi_to_gdf(
        self,
        df_bi: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """
            Transforming the accidents and bikes itinerary
            DataFrames into GeoDataFrames.
        """

        def make_line(row: pd.Series) -> LineString:
            return LineString([ # type: ignore
                (row["start_lng"], row["start_lat"]),
                (row["end_lng"], row["end_lat"]),
            ])

        df_bi["geometry"] = df_bi.apply(make_line, axis=1) # type: ignore

        gdf_bi = gpd.GeoDataFrame(
            df_bi,
            geometry="geometry",
            crs="EPSG:4326"
        )

        # Creating a buffer around the itinerary in meters
        gdf_bi = gdf_bi.to_crs("EPSG:32618")
        gdf_bi["geometry"] = gdf_bi.geometry.buffer(MATCHING_ACCIDENTS_RADIUS) # type: ignore
        gdf_bi = gdf_bi.to_crs("EPSG:4326")

        return gdf_bi

    def _clean_accidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """
            Cleaning the accidents DataFrame.
        """

        # Dropping the rows with missing MAIN values
        df.dropna(subset=[
            "CRASH DATE",
            "CRASH TIME",
            "LATITUDE",
            "LONGITUDE",
        ], inplace=True)

        # Converting the datetime column
        df["started_at"] = pd.to_datetime( # type: ignore
            df["CRASH DATE"] + " " + df["CRASH TIME"], # type: ignore
            format="%m/%d/%Y %H:%M",
            errors="coerce"
        )

        # Removing useless columns
        df.drop(columns=[  # type: ignore
            "CRASH DATE",
            "CRASH TIME",
            "LOCATION",
            "COLLISION_ID",
            "VEHICLE TYPE CODE 1",
            "VEHICLE TYPE CODE 2",
            "VEHICLE TYPE CODE 3",
            "VEHICLE TYPE CODE 4",
            "VEHICLE TYPE CODE 5",
        ], inplace=True)
        
        # Fixing the longitude and latitude columns
        df["LONGITUDE"] = ( 
            df["LONGITUDE"] # type: ignore
            .astype(str)
            .str
            .replace(",", ".")
            .astype(float)
        )
        df["LATITUDE"] = (
            df["LATITUDE"] # type: ignore
            .astype(str)
            .str.replace(",", ".")
            .astype(float)
        )
        df = df[(df["LONGITUDE"] != 0) | (df["LATITUDE"] != 0)] # type: ignore

        df.infer_objects()

        # Fixing index
        df.reset_index(drop=True, inplace=True)

        return df

    def _validate_monthly_period(self, df: pd.DataFrame) -> tuple[datetime, datetime]:
        """
            Getting the monthly period that the df is part of
            meaning the whole month(s). If it starts and end in mid of January
            than it means it will get from the first of January to the last of January.

            Then it will validate the number of months to import and raise an error
            if it is greater than {MAX_NB_MONTH_PER_IMPORT}.

            Params:
                - df: The pandas DataFrame to validate.

            Returns:
                - start_date: The start date of the dataframe.
                - end_date: The end date of the dataframe.

            Raises:
                - ValueError: If the number of months to import
                is greater than {MAX_NB_MONTH_PER_IMPORT} !
        """
        

        start_date = df["started_at"].min() # type: ignore
        start_date = start_date.to_period("M").start_time # type: ignore
        end_date = df["started_at"].max() + pd.offsets.MonthEnd(0) # type: ignore

        # Validating the number of months to import
        nb_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1 # type: ignore
        if nb_months > MAX_NB_MONTH_PER_IMPORT:
            raise ValueError(f"The number of months to import is greater than {MAX_NB_MONTH_PER_IMPORT} !")

        return start_date, end_date # type: ignore