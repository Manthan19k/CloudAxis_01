"""Pydantic schemas for monitoring metrics."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field


class MetricSampleBase(BaseModel):
    source: str = Field(..., max_length=120)
    metric: str = Field(..., max_length=64)
    value: float
    unit: Optional[str] = None
    recorded_at: Optional[dt.datetime] = None


class MetricSampleCreate(MetricSampleBase):
    pass


class MetricSampleOut(MetricSampleBase):
    id: int

    model_config = {"from_attributes": True}


class MetricSeries(BaseModel):
    metric: str
    points: List[MetricSampleOut]


class MetricTimelinePoint(BaseModel):
    t: str
    cpu: Optional[float] = None
    memory: Optional[float] = None
    network: Optional[float] = None
    storage: Optional[float] = None


class MetricTimelineResponse(BaseModel):
    series: str
    points: List[MetricTimelinePoint]