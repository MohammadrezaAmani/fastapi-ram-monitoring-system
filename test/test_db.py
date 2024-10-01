import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
import os
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from databases import Database

from monitor.conf import TABLE_NAME
from monitor.db import (
    add_ram_data_to_db,
    count_ram_data,
    create_table,
    get_average_ram,
    get_last_n_data_from_database,
)
from monitor.enums import Device, Ram, Sort


@pytest_asyncio.fixture
async def db():
    database = Database("sqlite:///./test_db.db")
    await database.connect()
    await create_table(database)
    yield database
    await database.disconnect()
    os.remove("./test_db.db")


@pytest_asyncio.fixture
async def fake_data(db):
    now = datetime.now()
    for i in range(10):
        await add_ram_data_to_db(
            db=db,
            total_mb=8000 + i,
            free_mb=4000 - i * 100,
            timestamp=now - timedelta(minutes=i),
            device=Device.internal,
        )


@pytest.mark.asyncio
async def test_add_ram_data_to_db(db):
    await add_ram_data_to_db(
        db=db,
        total_mb=16000,
        free_mb=8000,
        timestamp=datetime.now(),
        device=Device.internal,
    )

    result = await db.fetch_all(f"SELECT * FROM {TABLE_NAME}")
    assert len(result) == 1
    assert result[0][Ram.total_mb] == 16000
    assert result[0][Ram.free_mb] == 8000


@pytest.mark.asyncio
async def test_get_last_n_data_from_database(db, fake_data):
    result = await get_last_n_data_from_database(
        db=db,
        n=5,
        fields=[Ram.total_mb, Ram.free_mb],
        order=Sort.DESC,
        order_by=Ram.timestamp,
    )

    assert len(result) == 5
    assert result[0][Ram.total_mb] == 8000
    assert result[4][Ram.total_mb] == 8004


@pytest.mark.asyncio
async def test_count_ram_data(db, fake_data):
    count = await count_ram_data(db=db)
    assert count == 10


@pytest.mark.asyncio
async def test_get_average_ram(db, fake_data):
    avg_free = await get_average_ram(db=db, field=Ram.free_mb)

    assert avg_free == pytest.approx(3550.0, rel=1e-2)


@pytest.mark.asyncio
async def test_get_average_ram_with_time_limit(db, fake_data):
    start_time = datetime.now() - timedelta(minutes=5)
    avg_free = await get_average_ram(db=db, field=Ram.free_mb, start_time=start_time)

    assert avg_free > 3500.0
