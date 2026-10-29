"""Pydantic schemas for monitoring metrics."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MetricSampleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    source: str = Field(..., max_length=120)
    metric: str = Field(..., max_length=64)
    value: float
    unit: Optional[str] = None
    recorded_at: Optional[dt.datetime] = Field(default=None, alias="recordedAt")


class MetricSampleCreate(MetricSampleBase):
    pass


class MetricSampleOut(MetricSampleBase):
    id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MetricSeries(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    metric: str
    points: List[MetricSampleOut]


class MetricTimelinePoint(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    t: str
    cpu: Optional[float] = None
    memory: Optional[float] = None
    network: Optional[float] = None
    storage: Optional[float] = None


class MetricTimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    series: str
    points: List[MetricTimelinePoint]
