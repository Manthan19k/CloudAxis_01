"""Pydantic schemas for datastores."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DatastoreBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str = Field(..., max_length=120)
    type: str = Field(..., max_length=16)
    capacity_tb: float = Field(..., ge=0.1, alias="capacityTB")
    used_tb: float = Field(default=0.0, ge=0, alias="usedTB")
    status: str = Field(default="healthy")
    location: Optional[str] = None


class DatastoreCreate(DatastoreBase):
    ds_id: Optional[str] = Field(default=None, alias="dsId")


class DatastoreUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: Optional[str] = None
    type: Optional[str] = None
    capacity_tb: Optional[float] = Field(default=None, alias="capacityTB")
    used_tb: Optional[float] = Field(default=None, alias="usedTB")
    status: Optional[str] = None
    location: Optional[str] = None


class DatastoreOut(DatastoreBase):
    id: int
    ds_id: str = Field(..., alias="dsId")
    free_tb: float = Field(default=0.0, alias="freeTB")
    utilization_pct: float = Field(default=0.0, alias="utilizationPct")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DatastoreListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: List[DatastoreOut]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    pages: int
