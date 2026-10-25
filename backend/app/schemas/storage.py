"""Pydantic schemas for datastores."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DatastoreBase(BaseModel):
    name: str = Field(..., max_length=120)
    type: str = Field(..., max_length=16)
    capacity_tb: float = Field(..., ge=0.1)
    used_tb: float = Field(default=0.0, ge=0)
    status: str = Field(default="healthy")
    location: Optional[str] = None


class DatastoreCreate(DatastoreBase):
    ds_id: Optional[str] = None


class DatastoreUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    capacity_tb: Optional[float] = None
    used_tb: Optional[float] = None
    status: Optional[str] = None
    location: Optional[str] = None


class DatastoreOut(DatastoreBase):
    id: int
    ds_id: str
    free_tb: float = 0.0
    utilization_pct: float = 0.0

    model_config = {"from_attributes": True}


class DatastoreListResponse(BaseModel):
    items: List[DatastoreOut]
    total: int
    page: int
    page_size: int
    pages: int