import os
import sys
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from databases import Database
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from monitor.__init__ import app
from monitor.db import add_ram_data_to_db, create_table
from monitor.enums import Device

client = TestClient(app)


@pytest_asyncio.fixture
async def setup_db():
    database = Database("sqlite:///./test_db.db")
    await database.connect()
    await create_table(database)
    yield database
    await database.disconnect()
    os.remove("./test_db.db")


@pytest_asyncio.fixture
async def fake_data(setup_db):
    now = datetime.now()
    for i in range(10):
        await add_ram_data_to_db(
            db=setup_db,
            total_mb=8000 + i,
            free_mb=4000 - i * 100,
            timestamp=now - timedelta(minutes=i),
            device=Device.internal,
        )


@pytest.mark.asyncio
async def test_get_last_n_data(setup_db, fake_data):
    response = client.get("/ram?n=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_last_n_data_(setup_db, fake_data):
    response = client.get("/ram?n=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_last_n_data_sort_by_id(setup_db, fake_data):
    response = client.get("/ram?n=7&order_by=id")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    assert int(data[0]["id"]) <= int(data[1]["id"])


@pytest.mark.asyncio
async def test_get_last_n_data_sort_by_id_sort(setup_db, fake_data):
    response = client.get("/ram?n=7&order_by=id&order=DESC")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    assert int(data[0]["id"]) >= int(data[1]["id"])


@pytest.mark.asyncio
async def test_get_report(setup_db, fake_data):
    response = client.get("/")
    assert response.status_code == 200
    report = response.json()
    assert "avg_free" in report and report["avg_free"] is not None


@pytest.mark.asyncio
async def test_add_ram_data(setup_db, fake_data):
    payload = {"total_mb": 16000, "free_mb": 8000}
    response = client.post("/", json=payload)
    assert response.status_code == 201
