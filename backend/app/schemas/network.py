"""Pydantic schemas for network devices."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NetworkDeviceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str = Field(..., max_length=120)
    type: str = Field(..., max_length=32)
    vendor: Optional[str] = None
    ip: Optional[str] = None
    throughput_gbps: float = Field(default=0.0, ge=0, alias="throughputGbps")
    latency_ms: float = Field(default=0.0, ge=0, alias="latencyMs")
    packet_loss: float = Field(default=0.0, ge=0, le=100, alias="packetLoss")
    status: str = Field(default="healthy")


class NetworkDeviceCreate(NetworkDeviceBase):
    dev_id: Optional[str] = Field(default=None, alias="devId")


class NetworkDeviceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: Optional[str] = None
    type: Optional[str] = None
    vendor: Optional[str] = None
    ip: Optional[str] = None
    throughput_gbps: Optional[float] = Field(default=None, alias="throughputGbps")
    latency_ms: Optional[float] = Field(default=None, alias="latencyMs")
    packet_loss: Optional[float] = Field(default=None, alias="packetLoss")
    status: Optional[str] = None


class NetworkDeviceOut(NetworkDeviceBase):
    id: int
    dev_id: str = Field(..., alias="devId")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NetworkDeviceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: List[NetworkDeviceOut]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    pages: int
