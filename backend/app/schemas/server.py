"""Pydantic schemas for physical servers."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ServerBase(BaseModel):
    name: str = Field(..., max_length=120)
    ip: str = Field(..., max_length=45)
    location: str = Field(..., max_length=64)
    rack: Optional[str] = None
    os: Optional[str] = None
    cpu: float = Field(default=0.0, ge=0, le=100)
    memory: float = Field(default=0.0, ge=0)
    storage: float = Field(default=0.0, ge=0, le=100)
    temperature: float = Field(default=0.0, ge=-40, le=120)
    status: str = Field(default="healthy")
    owner: Optional[str] = None
    department: Optional[str] = None
    vm_count: int = Field(default=0, ge=0)
    uptime_days: int = Field(default=0, ge=0)


class ServerCreate(ServerBase):
    server_id: Optional[str] = None


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    ip: Optional[str] = None
    location: Optional[str] = None
    rack: Optional[str] = None
    os: Optional[str] = None
    cpu: Optional[float] = None
    memory: Optional[float] = None
    storage: Optional[float] = None
    temperature: Optional[float] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    vm_count: Optional[int] = None
    uptime_days: Optional[int] = None


class ServerOut(ServerBase):
    id: int
    server_id: str

    model_config = {"from_attributes": True}


class ServerListResponse(BaseModel):
    items: List[ServerOut]
    total: int
    page: int
    page_size: int
    pages: int