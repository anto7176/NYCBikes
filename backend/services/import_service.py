#
#   Imports
#

import uuid
import io
import pandas as pd # type: ignore
import geopandas as gpd # type: ignore

from datetime import datetime
from typing import Any, List
from pymongo import AsyncMongoClient
from fastapi.datastructures import UploadFile
from pymongo.errors import BulkWriteError

# Perso

from enums.import_types import ImportType

#
#   Constants
#

BATCH_SIZE = 10000
BIKES_ITINERARY_DIVIDER_RATIO = 30
MATCHING_ACCIDENTS_RADIUS = 100

#
#   Services
#

class ImportService:
    """
        Service to import collections to the database.
    """

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db["nycbikes"]

    async def import_collection(self, import_type: ImportType, file: UploadFile):
        """
            Import a collection from a CSV file.
        """

        # Reading the file
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        if df.empty:
            raise ValueError("No data found in the file !")
        await file.close()

        # Importing the collection
        if import_type == ImportType.ACCIDENTS:
            await self.import_accidents(df)
        elif import_type == ImportType.BIKES_ITINERARY:
            await self.import_bikes_itinerary(df)

    async def import_accidents(self, df: pd.DataFrame):
        """
            Import accidents from a pandas DataFrame.
        """

        df = self._clean_accidents(df)

        #
        #   Processing the DataFrame
        #

        # Adding the UUID to the DataFrame
        df["acc_id"] = [uuid.uuid4() for _ in range(len(df))]

        sdate, edate = self._get_monthly_period(df)

        # Getting from the database the bikes itinerary
        # and accidents for the given period
        db_df_bi, db_df_acc = await self._get_bi_acc_from_period(
            sdate, edate
        )

        # Concatenating the db accidents and the bikes ones
        # from the same period and ignoring the duplicates.
        # But it ignores by comparing the values and not the
        # ids as it is new ids for the new possibly new accidents.
        df_acc = pd.concat([db_df_acc, df], ignore_index=True)
        df_acc.drop_duplicates(
            subset=[col for col in df_acc.columns if col != "acc_id"], # type: ignore
            inplace=True
        )

        if not db_df_bi.empty:
            gdf_acc, db_gdf_bi = self._transform_acc_bi_to_gdf(df_acc, db_df_bi)

            # Getting the new bikes itinerary df by calculating
            # the matching between the accidents and the bikes itinerary
            df_bi = self._match_accidents(gdf_acc, db_gdf_bi, MATCHING_ACCIDENTS_RADIUS)

            # Inserting the new bikes itinerary into the database
            await self._batch_insert(df_bi, "bikes_itinerary")

        # Inserting the new accidents into the database
        await self._batch_insert(df_acc, "accidents")

    async def import_bikes_itinerary(self, df: pd.DataFrame):
        """
            Import bikes itinerary from a pandas DataFrame.
        """

        df = self._clean_bikes_itinerary(df)

        #
        #   Processing the DataFrame
        #
        
        # Adding the UUID to the DataFrame
        df["bi_id"] = [uuid.uuid4() for _ in range(len(df))]

        # Adding the accident_ids column
        df["accident_ids"] = [[] for _ in range(len(df))]

        sdate, edate = self._get_monthly_period(df)

        # Getting from the database the bikes itinerary
        # and accidents for the given period
        db_df_bi, db_df_acc = await self._get_bi_acc_from_period(
            sdate, edate
        )

        # Concatenating the db bikes itinerary and the new ones
        # from the same period and ignoring the duplicates.
        # But it ignores the by comparing the values and not the
        # ids as it is new ids for the new possibly new bikes itinerary.
        df_bi = pd.concat([db_df_bi, df], ignore_index=True)
        df_bi.drop_duplicates(
            subset=[col for col in df_bi.columns if col != "bi_id" and col != "accident_ids"], # type: ignore
            inplace=True
        )

        if not db_df_acc.empty:
            gdb_df_acc, db_gdf_bi = self._transform_acc_bi_to_gdf(db_df_acc, df_bi)

            # Getting the new bikes itinerary df by calculating
            # the matching between the accidents and the bikes itinerary
            df_bi = self._match_accidents(gdb_df_acc, db_gdf_bi, MATCHING_ACCIDENTS_RADIUS)

            # Inserting the new accidents into the database
            await self._batch_insert(db_df_acc, "accidents")

        # Inserting the new bikes itinerary into the database
        await self._batch_insert(df_bi, "bikes_itinerary")

    async def _batch_insert(
        self,
        df: pd.DataFrame,
        coll_name: str
    ) -> None:
        """
            Batch inserts the rows in the database

            Params:
                - df: The df to insert
                - coll_name : The name of the collection to insert in.
        """
        
        df = df.drop(columns=["_id"], errors="ignore") # type: ignore
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
            "ride_id",
            "start_station_id",
            "end_station_id",
        ], inplace=True)
        
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
        df = df.sample(n=len(df) // BIKES_ITINERARY_DIVIDER_RATIO) # type: ignore

        return df

    def _transform_acc_bi_to_gdf(
        self,
        df_acc: pd.DataFrame,
        df_bi: pd.DataFrame
    ) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """
            Transforming the accidents and bikes itinerary
            DataFrames into GeoDataFrames.
        """

        gdf_acc = gpd.GeoDataFrame(
            df_acc,
            geometry=gpd.points_from_xy(
                df_acc["LONGITUDE"], # type: ignore
                df_acc["LATITUDE"], # type: ignore
            ),
            crs="EPSG:4326"
        ).to_crs("EPSG:32618")

        gdf_bi = gpd.GeoDataFrame(
            df_bi,
            geometry=gpd.points_from_xy(
                df_bi["start_lng"], # type: ignore
                df_bi["start_lat"], # type: ignore
            ),
            crs="EPSG:4326"
        ).to_crs("EPSG:32618")

        return gdf_acc, gdf_bi

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

    def _get_monthly_period(self, df: pd.DataFrame) -> tuple[datetime, datetime]:
        """
            Getting the monthly period that the df is part of
            meaning the whole month(s).

            It is meant to be used in the imports ot get the monthmy period
            of the imported data and hence get already existring data in the
            database from bikes and accidents to then calculate the matching
            between them.
        """

        start_date = df["started_at"].min() # type: ignore
        start_date = start_date.to_period("M").start_time # type: ignore
        end_date = df["started_at"].max() + pd.offsets.MonthEnd(0) # type: ignore

        return start_date, end_date # type: ignore


    async def _get_bi_acc_from_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
            Getting from the database the bikes itinerary
            and accidents for the given period.
        """

        QUERY = {
            "started_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        db_bikes_itinerary = await self._db["bikes_itinerary"].find(QUERY).to_list()

        db_accidents = await self._db["accidents"].find(QUERY).to_list()

        db_bikes_itinerary = pd.DataFrame(db_bikes_itinerary) # type: ignore
        db_accidents = pd.DataFrame(db_accidents) # type: ignore

        return db_bikes_itinerary, db_accidents # type: ignore


    def _match_accidents(
        self,
        gdf_acc: gpd.GeoDataFrame,
        gdf_bi: gpd.GeoDataFrame,
        radius: float
    ) -> pd.DataFrame:
        """
            Matches the accidents present in a given rayon
            of the bikes itinerary to the bikes itinerary accident
            ids list.
        """

        # Adding the itinerary corridor to the bikes itinerary
        # meaning a tube around the itinerary representing the radius
        gdf_bi["itinerary_corridor"] = gdf_bi.geometry.buffer(radius) # type: ignore
        gdf_bi_corr = gdf_bi.set_geometry("itinerary_corridor")

        # Joining the bikes itinerary with the accidents
        # using the criteria that the accident must be inside the itinerary corridor
        bi_acc_joined = gpd.sjoin(
            gdf_bi_corr[["bi_id", "itinerary_corridor"]], # type: ignore
            gdf_acc[["acc_id", "geometry"]], # type: ignore
            how="inner",
            predicate="intersects"
        )

        # Grouping the accidents by bikes itinerary
        # and getting the list of accident ids for each bikes itinerary
        bi_list_accident_ids = ( # type: ignore
            bi_acc_joined
            .groupby("bi_id")["acc_id"] # type: ignore
            .agg(list)
            .reset_index()
            .rename(columns={"acc_id": "accident_ids"})
        )

        # Merging the bikes itinerary with the list of accident ids
        df_bi = gdf_bi.merge(
            bi_list_accident_ids, # type: ignore
            on="bi_id",
            how="left",
        )

        # Dropping the geometry columns
        df_bi.drop(columns=["geometry", "itinerary_corridor"], inplace=True) # type: ignore

        return df_bi