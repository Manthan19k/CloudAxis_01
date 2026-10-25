"""Pydantic schemas for alerts."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    severity: str = Field(..., max_length=16)
    title: str = Field(..., max_length=255)
    source: Optional[str] = None
    assignee: Optional[str] = None


class AlertCreate(AlertBase):
    alert_id: Optional[str] = None
    triggered_at: Optional[dt.datetime] = None


class AlertUpdate(BaseModel):
    severity: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    assignee: Optional[str] = None
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None


class AlertOut(AlertBase):
    id: int
    alert_id: str
    triggered_at: dt.datetime
    acknowledged: bool
    resolved: bool

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    items: List[AlertOut]
    total: int
    page: int
    page_size: int
    pages: int