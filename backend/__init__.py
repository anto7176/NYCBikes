"""
    Backend package initializer.

    This file contains a cron-like for API-to-database imports.
"""

import asyncio
from datetime import date, datetime, timedelta, time

from backend.config.config import get_settings

settings = get_settings()

async def sleep_until_next_local_run(run_time: time) -> None:
    now = datetime.now()
    next_run = datetime.combine(now.date(), run_time)
    if next_run <= now:
        next_run = next_run + timedelta(days=1)

    seconds = (next_run - now).total_seconds()
    await asyncio.sleep(seconds)


async def import_job_once() -> None:
    today = date.today()
    start_date = date(today.year, today.month, 1)

    first_of_next_month = (
        start_date.replace(day=28) + timedelta(days=4)
    ).replace(day=1)

    service = ApiImportService(get_db()) # type: ignore
    await service.import_from_apis( # type: ignore
        start_date=start_date,
        end_date=first_of_next_month,
    )

