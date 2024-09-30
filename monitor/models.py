from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field


class RamMonitorIn(BaseModel):
    total_mb: int
    free_mb: int
    timestamp: Optional[datetime] = None


class RamMonitorOut(RamMonitorIn):
    id: int

    @computed_field
    @property
    def used_mb(self) -> int:
        return self.total_mb - self.free_mb


class Report(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    avg_free: float
    count: int
