"""Pydantic schemas for virtual machines."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class VMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str = Field(..., max_length=120)
    host_name: Optional[str] = Field(default=None, alias="host")
    host_id: Optional[int] = Field(default=None, alias="hostId")
    os: Optional[str] = None
    v_cpu: int = Field(default=2, ge=1, le=128, alias="vCPU")
    memory_gb: int = Field(default=4, ge=1, le=512, alias="memoryGB")
    disk_gb: int = Field(default=40, ge=1, le=2048, alias="diskGB")
    cpu: float = Field(default=0.0, ge=0, le=100)
    memory: float = Field(default=0.0, ge=0)
    status: str = Field(default="healthy")
    ip: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    snapshots: int = Field(default=0, ge=0)


class VMCreate(VMBase):
    vm_id: Optional[str] = Field(default=None, alias="vmId")


class VMUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: Optional[str] = None
    host_name: Optional[str] = Field(default=None, alias="host")
    host_id: Optional[int] = Field(default=None, alias="hostId")
    os: Optional[str] = None
    v_cpu: Optional[int] = Field(default=None, alias="vCPU")
    memory_gb: Optional[int] = Field(default=None, alias="memoryGB")
    disk_gb: Optional[int] = Field(default=None, alias="diskGB")
    cpu: Optional[float] = None
    memory: Optional[float] = None
    status: Optional[str] = None
    ip: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    snapshots: Optional[int] = None


class VMOut(VMBase):
    id: int
    vm_id: str = Field(..., alias="vmId")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class VMListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: List[VMOut]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    pages: int
