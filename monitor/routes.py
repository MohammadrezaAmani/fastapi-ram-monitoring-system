from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, Response, status

from monitor.conf import DEFAULT_N, DEFAULT_ORDER_BY, DEFAULT_SORT
from monitor.controllers import add_ram_data, get_last_n_data, get_report
from monitor.enums import Ram, safe
from monitor.models import RamMonitorIn, RamMonitorOut, Report

router = APIRouter()


@router.get("/", response_model=Report)
async def root(
    start_time: datetime | None = Query(None, description="Start of time limit"),
    end_time: datetime | None = Query(None, description="End of time limit"),
):
    return await get_report(start_time=start_time, end_time=end_time)


@router.get("/ram/", response_model=List[RamMonitorOut])
async def read_ram_data(
    order: str = Query(DEFAULT_SORT, description="Number of latest records"),
    n: int = Query(DEFAULT_N, description="Number of latest records"),
    order_by: str = Query(DEFAULT_ORDER_BY, description="Number of latest records"),
    start_time: datetime | None = Query(None, description="Number of latest records"),
    end_time: datetime | None = Query(None, description="Number of latest records"),
):
    data = await get_last_n_data(
        order=order,
        n=n,
        fields=safe(Ram),
        order_by=order_by,
        start_time=start_time,
        end_time=end_time,
    )
    return data


@router.post("/ram/")
async def add_data(data: RamMonitorIn):
    try:
        await add_ram_data(**data)  # type: ignore
        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as err:
        return Response({"err": str(err)}, status_code=status.HTTP_400_BAD_REQUEST)
