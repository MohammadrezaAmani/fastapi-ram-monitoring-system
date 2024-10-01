import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

import psutil
from databases import Database

from monitor.conf import SLEEP_TIME
from monitor.db import (
    add_ram_data_to_db,
    count_ram_data,
    create_table,
    get_average_ram,
    get_db,
    get_last_n_data_from_database,
)
from monitor.enums import Device, Ram, Sort, safe
from monitor.models import RamMonitorIn, RamMonitorOut, Report


@asynccontextmanager
async def lifespan(app):
    db = get_db()
    await db.connect()
    task = asyncio.create_task(start_database(db))
    yield
    task.cancel()
    await db.disconnect()


async def log_ram_data(
    db: Database,
):
    ram_info = psutil.virtual_memory()
    total_mb = ram_info.total // (1024 * 1024)
    free_mb = ram_info.free // (1024 * 1024)

    await add_ram_data_to_db(
        total_mb=total_mb, free_mb=free_mb, device=Device.internal, db=db
    )


async def get_last_n_data(
    db: Database,
    n: int,
    fields: List[str] = safe(Ram),
    order_by: str = Ram.timestamp,
    order: str = Sort.DESC,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> List[RamMonitorOut]:
    return [
        RamMonitorOut(**record)  # type: ignore
        for record in await get_last_n_data_from_database(
            n=n,
            fields=fields,
            order=order,
            order_by=order_by,
            start_time=start_time,
            end_time=end_time,
            db=db,
        )
    ]


async def get_report(
    db: Database,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    field: str = Ram.free_mb,
) -> Report:
    return Report(
        start_time=start_time,
        end_time=end_time,
        avg_free=await get_average_ram(
            field=field, start_time=start_time, end_time=end_time, db=db
        ),
        count=await count_ram_data(start_time=start_time, end_time=end_time, db=db),
    )


async def start_database(
    db: Database,
):
    await create_table(db=db)
    await start_logging(db)


async def add_ram_data(
    db: Database,
    data: RamMonitorIn,
):
    return await add_ram_data_to_db(**data.model_dump(), device=Device.external, db=db)


async def start_logging(
    db: Database,
):
    while True:
        await log_ram_data(db)
        await asyncio.sleep(SLEEP_TIME)
