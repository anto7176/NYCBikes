"""
    Service for fast API-to-database imports.

    This module provides a good starting point for importing:
    - Bikes itinerary data (endpoint not fixed in this project)
    - Accidents data from the NYC Socrata API view h9gi-nx95

    The mapping from API fields to your expected pandas columns will likely
    need to be adapted depending on the exact API response shape.
"""

import asyncio
import json
import re
import urllib.request
import urllib.parse

import pandas as pd  # type: ignore

from datetime import date, datetime
from typing import Any, Optional

from config.config import get_settings
from services.import_service import ImportService
from services.matching_service import MatchingService

settings = get_settings()


class ApiImportService:
    """
        Quick import service that fetches remote API JSON, normalizes it into
        pandas DataFrames, then reuses your existing ImportService logic.
    """

    def __init__(self, db: Any):
        self._import_service = ImportService(db)
        self._matching_service = MatchingService(db)

    async def import_from_apis(
        self,
        start_date: date,
        end_date: date,
        accidents_limit: int = 50000,
        bikes_limit: Optional[int] = None,
    ) -> tuple[datetime, datetime]:
        """
            Import bikes itinerary and accidents from API endpoints, then
            match accidents to bikes itineraries for the overlapping period.
        """

        bikes_records = await self._fetch_bikes_itinerary_records(
            start_date=start_date,
            end_date=end_date,
            limit=bikes_limit,
        )
        accidents_records = await self._fetch_accidents_records(
            start_date=start_date,
            end_date=end_date,
            limit=accidents_limit,
        )

        bikes_df = self._normalize_bikes_records_to_df(bikes_records)
        accidents_df = self._normalize_accidents_records_to_df(
            accidents_records
        )

        bikes_start, bikes_end = await self._import_service.import_bikes_itinerary(
            bikes_df
        )
        acc_start, acc_end = await self._import_service.import_accidents(
            accidents_df
        )

        matching_start = max(bikes_start, acc_start)
        matching_end = min(bikes_end, acc_end)

        if matching_start >= matching_end:
            return matching_start, matching_end

        await self._matching_service.match_acc_bi_by_month(
            matching_start,
            matching_end,
        )

        return matching_start, matching_end

    async def _fetch_json(
        self,
        url: str,
        method: str = "GET",
        payload: Optional[dict[str, Any]] = None,
        timeout_s: int = 60,
    ) -> Any:
        def _do_fetch() -> Any:
            body_bytes: Optional[bytes] = None
            headers = {"User-Agent": "nycbikes-import/0.1"}

            if payload is not None:
                body_bytes = json.dumps(payload).encode("utf-8")
                headers["Content-Type"] = "application/json"

            req = urllib.request.Request(url, method=method, headers=headers)
            if body_bytes is not None:
                req.data = body_bytes  # type: ignore[attr-defined]

            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read()

            decoded = raw.decode("utf-8", errors="replace")
            return json.loads(decoded)

        return await asyncio.to_thread(_do_fetch)

    def _fetch_records_list(
        self,
        obj: Any,
    ) -> list[dict[str, Any]]:
        if obj is None:
            return []

        if isinstance(obj, list):
            return [r for r in obj if isinstance(r, dict)] # type: ignore

        if not isinstance(obj, dict):
            return []

        data = obj.get("data") # type: ignore
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)] # type: ignore

        if isinstance(data, dict):
            for key in ("rows", "records", "results"):
                nested = data.get(key) # type: ignore
                if isinstance(nested, list):
                    return [r for r in nested if isinstance(r, dict)] # type: ignore

        for key in ("rows", "records", "results"):
            nested = obj.get(key) # type: ignore
            if isinstance(nested, list):
                return [r for r in nested if isinstance(r, dict)] # type: ignore

        return []

    async def _fetch_bikes_itinerary_records(
        self,
        start_date: date,
        end_date: date,
        limit: Optional[int],
    ) -> list[dict[str, Any]]:
        bikes_url = getattr(
            settings,
            "BIKES_ITINERARY_API_URL",
            "",
        )

        if not bikes_url:
            # Endpoint not specified in the current project.
            return []

        params: dict[str, Any] = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        if limit is not None:
            params["limit"] = limit

        url = bikes_url
        joiner = "&" if "?" in bikes_url else "?"
        url = f"{url}{joiner}{urllib.parse.urlencode(params)}"

        obj = await self._fetch_json(url=url, method="GET")
        return self._fetch_records_list(obj)

    async def _fetch_accidents_records(
        self,
        start_date: date,
        end_date: date,
        limit: int,
    ) -> list[dict[str, Any]]:
        accidents_url = (
            "https://data.cityofnewyork.us/api/v3/"
            "views/h9gi-nx95/query.json"
        )

        payload = {
            "select": "*",
            "limit": limit,
            "where": (
                f"crash_date >= \"{start_date.isoformat()}\" "
                f"AND crash_date < \"{end_date.isoformat()}\""
            ),
        }

        obj = await self._fetch_json(
            url=accidents_url,
            method="POST",
            payload=payload,
        )
        return self._fetch_records_list(obj)

    @staticmethod
    def _normalize_column_name(name: str) -> str:
        lowered = name.strip().lower()
        return re.sub(r"[^a-z0-9]+", "", lowered)

    def _find_first_column(
        self,
        df: pd.DataFrame,
        candidates: list[str],
    ) -> Optional[str]:
        if df.empty:
            return None

        normalized = { # type: ignore
            self._normalize_column_name(col): col for col in df.columns # type: ignore
        }
        for cand in candidates:
            key = self._normalize_column_name(cand)
            if key in normalized:
                return normalized[key] # type: ignore

        return None

    def _normalize_bikes_records_to_df(
        self,
        records: list[dict[str, Any]],
    ) -> pd.DataFrame:
        df_raw = pd.DataFrame(records)
        df_out = pd.DataFrame()

        # Ride identifier (ImportService expects "ride_id").
        df_out["ride_id"] = self._extract_or_none(
            df_raw,
            ["ride_id", "rideid", "rideId", "trip_id", "tripId", "id", "_id"],
            len(records),
        )

        df_out["started_at"] = self._extract_or_none(
            df_raw,
            ["started_at", "start_time", "startTime", "startedat", "startTime"],
            len(records),
        )
        df_out["ended_at"] = self._extract_or_none(
            df_raw,
            ["ended_at", "end_time", "endTime", "endedat", "endTime"],
            len(records),
        )

        df_out["start_lat"] = self._extract_or_none(
            df_raw,
            ["start_lat", "startLat", "start_latitude", "startlatitude", "lat"],
            len(records),
        )
        df_out["start_lng"] = self._extract_or_none(
            df_raw,
            ["start_lng", "startLng", "start_longitude", "startlongitude", "lng", "lon"],
            len(records),
        )
        df_out["end_lat"] = self._extract_or_none(
            df_raw,
            ["end_lat", "endLat", "end_latitude", "endlatitude", "endlat"],
            len(records),
        )
        df_out["end_lng"] = self._extract_or_none(
            df_raw,
            ["end_lng", "endLng", "end_longitude", "endlongitude", "endlng", "endlon"],
            len(records),
        )

        df_out["start_station_name"] = self._extract_or_none(
            df_raw,
            [
                "start_station_name",
                "startstationname",
                "from_station_name",
                "fromstationname",
            ],
            len(records),
        )
        df_out["end_station_name"] = self._extract_or_none(
            df_raw,
            [
                "end_station_name",
                "endstationname",
                "to_station_name",
                "tostationname",
            ],
            len(records),
        )

        # ImportService drops those columns, but they must exist.
        df_out["start_station_id"] = self._extract_or_none(
            df_raw,
            ["start_station_id", "startstationid", "from_station_id", "fromstationid"],
            len(records),
        )
        df_out["end_station_id"] = self._extract_or_none(
            df_raw,
            ["end_station_id", "endstationid", "to_station_id", "tostationid"],
            len(records),
        )

        return df_out

    def _normalize_accidents_records_to_df(
        self,
        records: list[dict[str, Any]],
    ) -> pd.DataFrame:
        df_raw = pd.DataFrame(records)
        df_out = pd.DataFrame()

        df_out["CRASH DATE"] = self._extract_or_none(
            df_raw,
            ["crash date", "crash_date", "crashdate"],
            len(records),
        )
        df_out["CRASH TIME"] = self._extract_or_none(
            df_raw,
            ["crash time", "crash_time", "crashtime"],
            len(records),
        )
        df_out["LATITUDE"] = self._extract_or_none(
            df_raw,
            ["latitude", "LATITUDE", "lat"],
            len(records),
        )
        df_out["LONGITUDE"] = self._extract_or_none(
            df_raw,
            ["longitude", "LONGITUDE", "lng", "lon"],
            len(records),
        )

        # ImportService drops those columns, but they must exist.
        df_out["LOCATION"] = self._extract_or_none(
            df_raw,
            ["location", "LOCATION"],
            len(records),
        )
        df_out["COLLISION_ID"] = self._extract_or_none(
            df_raw,
            ["collision_id", "collisionid", "COLLISION_ID"],
            len(records),
        )
        df_out["VEHICLE TYPE CODE 1"] = self._extract_or_none(
            df_raw,
            ["vehicle type code 1", "vehicletypecode1", "vehicletype1"],
            len(records),
        )
        df_out["VEHICLE TYPE CODE 2"] = self._extract_or_none(
            df_raw,
            ["vehicle type code 2", "vehicletypecode2", "vehicletype2"],
            len(records),
        )
        df_out["VEHICLE TYPE CODE 3"] = self._extract_or_none(
            df_raw,
            ["vehicle type code 3", "vehicletypecode3", "vehicletype3"],
            len(records),
        )
        df_out["VEHICLE TYPE CODE 4"] = self._extract_or_none(
            df_raw,
            ["vehicle type code 4", "vehicletypecode4", "vehicletype4"],
            len(records),
        )
        df_out["VEHICLE TYPE CODE 5"] = self._extract_or_none(
            df_raw,
            ["vehicle type code 5", "vehicletypecode5", "vehicletype5"],
            len(records),
        )

        return df_out

    def _extract_or_none(
        self,
        df_raw: pd.DataFrame,
        candidates: list[str],
        length: int,
    ) -> pd.Series:
        col = self._find_first_column(df_raw, candidates)
        if col is None:
            return pd.Series([None] * length)
        return df_raw[col] # type: ignore

