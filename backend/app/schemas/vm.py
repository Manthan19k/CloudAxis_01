"""Pydantic schemas for virtual machines."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class VMBase(BaseModel):
    name: str = Field(..., max_length=120)
    host_name: Optional[str] = None
    host_id: Optional[int] = None
    os: Optional[str] = None
    v_cpu: int = Field(default=2, ge=1, le=128)
    memory_gb: int = Field(default=4, ge=1, le=512)
    disk_gb: int = Field(default=40, ge=1, le=2048)
    cpu: float = Field(default=0.0, ge=0, le=100)
    memory: float = Field(default=0.0, ge=0)
    status: str = Field(default="healthy")
    ip: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    snapshots: int = Field(default=0, ge=0)


class VMCreate(VMBase):
    vm_id: Optional[str] = None


class VMUpdate(BaseModel):
    name: Optional[str] = None
    host_name: Optional[str] = None
    host_id: Optional[int] = None
    os: Optional[str] = None
    v_cpu: Optional[int] = None
    memory_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    cpu: Optional[float] = None
    memory: Optional[float] = None
    status: Optional[str] = None
    ip: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    snapshots: Optional[int] = None


class VMOut(VMBase):
    id: int
    vm_id: str

    model_config = {"from_attributes": True}


class VMListResponse(BaseModel):
    items: List[VMOut]
    total: int
    page: int
    page_size: int
    pages: int