"""Pydantic schemas for network devices."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class NetworkDeviceBase(BaseModel):
    name: str = Field(..., max_length=120)
    type: str = Field(..., max_length=32)
    vendor: Optional[str] = None
    ip: Optional[str] = None
    throughput_gbps: float = Field(default=0.0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0)
    packet_loss: float = Field(default=0.0, ge=0, le=100)
    status: str = Field(default="healthy")


class NetworkDeviceCreate(NetworkDeviceBase):
    dev_id: Optional[str] = None


class NetworkDeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    vendor: Optional[str] = None
    ip: Optional[str] = None
    throughput_gbps: Optional[float] = None
    latency_ms: Optional[float] = None
    packet_loss: Optional[float] = None
    status: Optional[str] = None


class NetworkDeviceOut(NetworkDeviceBase):
    id: int
    dev_id: str

    model_config = {"from_attributes": True}


class NetworkDeviceListResponse(BaseModel):
    items: List[NetworkDeviceOut]
    total: int
    page: int
    page_size: int
    pages: int