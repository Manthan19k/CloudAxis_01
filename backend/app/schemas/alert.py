"""Pydantic schemas for alerts."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AlertBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    severity: str = Field(..., max_length=16)
    title: str = Field(..., max_length=255)
    source: Optional[str] = None
    assignee: Optional[str] = None


class AlertCreate(AlertBase):
    alert_id: Optional[str] = Field(default=None, alias="alertId")
    triggered_at: Optional[dt.datetime] = Field(default=None, alias="triggeredAt")


class AlertUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    severity: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    assignee: Optional[str] = None
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None


class AlertOut(AlertBase):
    id: int
    alert_id: str = Field(..., alias="alertId")
    triggered_at: dt.datetime = Field(..., alias="triggeredAt")
    acknowledged: bool
    resolved: bool
    time: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="after")
    def populate_time_string(self) -> AlertOut:
        if self.time is None and self.triggered_at:
            self.time = (
                self.triggered_at.strftime("%H:%M:%S")
                if hasattr(self.triggered_at, "strftime")
                else str(self.triggered_at)[11:19]
            )
        return self


class AlertListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: List[AlertOut]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    pages: int
