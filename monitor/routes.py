from datetime import datetime
from typing import List

from databases import Database
from fastapi import APIRouter, Depends, Query, status

from monitor.conf import DEFAULT_N, DEFAULT_ORDER_BY, DEFAULT_SORT
from monitor.controllers import add_ram_data, get_last_n_data, get_report
from monitor.db import get_db
from monitor.enums import Ram, safe
from monitor.models import RamMonitorIn, RamMonitorOut, Report

router = APIRouter()


@router.get("/", response_model=Report)
async def root(
    start_time: datetime | None = Query(None, description="Start of time limit"),
    end_time: datetime | None = Query(None, description="End of time limit"),
    db: Database = Depends(get_db),
):
    return await get_report(start_time=start_time, end_time=end_time, db=db)


@router.get("/ram/", response_model=List[RamMonitorOut])
async def read_ram_data(
    order: str = Query(DEFAULT_SORT, description="Order of records"),
    n: int = Query(DEFAULT_N, description="Number of latest records", ge=0, le=1000),
    order_by: str = Query(DEFAULT_ORDER_BY, description="Order by which field"),
    start_time: datetime | None = Query(None, description="Start time limit"),
    end_time: datetime | None = Query(None, description="End time limit"),
    db: Database = Depends(get_db),
):
    return await get_last_n_data(
        order=order,
        n=n,
        fields=safe(Ram),
        order_by=order_by,
        start_time=start_time,
        end_time=end_time,
        db=db,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ram_data(
    data: RamMonitorIn,
    db: Database = Depends(get_db),
):
    return await add_ram_data(data=data, db=db)
