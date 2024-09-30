from datetime import datetime
from typing import Any, List, Optional

from databases import Database
from databases.interfaces import Record

from monitor.conf import DATABASE_URL, TABLE_NAME
from monitor.enums import Device, Ram, Sort, safe


async def create_table():
    query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                {Ram.id} INTEGER PRIMARY KEY AUTOINCREMENT, 
                {Ram.total_mb} INTEGER, 
                {Ram.free_mb} INTEGER,
                {Ram.device} INTEGER,
                {Ram.timestamp} DATETIME DEFAULT CURRENT_TIMESTAMP)
            """
    await get_db().execute(query=query)


async def add_ram_data_to_db(
    total_mb: int,
    free_mb: int,
    timestamp: Optional[datetime] = None,
    device: int = Device.internal,
):
    if timestamp is None:
        timestamp = datetime.now()
    query = f"""INSERT INTO {TABLE_NAME} (
                {Ram.total_mb},
                {Ram.free_mb},
                {Ram.timestamp},
                {Ram.device})
               VALUES (
                   :{Ram.total_mb},
                   :{Ram.free_mb},
                   :{Ram.timestamp},
                   :{Ram.device}
                )
            """

    values = {
        Ram.total_mb: total_mb,
        Ram.free_mb: free_mb,
        Ram.timestamp: timestamp,
        Ram.device: device,
    }
    await get_db().execute(query=query, values=values)


async def get_last_n_data_from_datebase(
    n: int,
    fields: List[str] = safe(Ram),
    order_by: str = Ram.timestamp,
    order: str = Sort.DESC,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> List[Record]:
    for i in fields:
        if i not in safe(Ram):
            raise
    fields_str = ", ".join(fields)
    time_limit_query, values = time_limit(start_time, end_time)
    query = f"""SELECT {fields_str} FROM {TABLE_NAME}
                {time_limit_query}
                ORDER BY {order_by} {order} LIMIT :n
            """
    values["n"] = n
    return await get_db().fetch_all(query=query, values=values)


async def count_ram_data(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> int:
    time_limit_query, values = time_limit(start_time, end_time)
    query = f"SELECT COUNT(*) FROM {TABLE_NAME} {time_limit_query}"
    result = await get_db().fetch_one(query=query, values=values)
    return result[0] if result else 0


async def get_average_ram(
    field: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> float:
    if field not in [Ram.total_mb, Ram.free_mb]:
        raise ValueError(f"Invalid field for average calculation: {field}")
    time_limit_query, values = time_limit(start_time, end_time)
    query = f"SELECT AVG({field}) FROM {TABLE_NAME} {time_limit_query}"
    result = await get_db().fetch_one(query=query, values=values)
    return result[0] if result else 0.0


def time_limit(
    start_time: datetime | None = None, end_time: datetime | None = None
) -> tuple[str, dict[str, Any]]:
    return (
        (
            f"WHERE {Ram.timestamp} BETWEEN :start_time AND :end_time",
            {"end_time": end_time, "start_time": start_time},
        )
        if (start_time and end_time)
        else (
            (f"WHERE {Ram.timestamp} >= :start_time", {"start_time": start_time})
            if start_time
            else (
                (f"WHERE {Ram.timestamp} <= :end_time", {"end_time": end_time})
                if end_time
                else ("", {})
            )
        )
    )


database = Database(DATABASE_URL)


def get_db() -> Database:
    return database
