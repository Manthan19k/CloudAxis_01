"""Pydantic schemas for health and dashboard summaries."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str
    environment: str
    database: str = "unknown"


class DashboardSummary(BaseModel):
    health_score: int
    total_servers: int
    healthy_servers: int
    total_vms: int
    healthy_vms: int
    total_datastores: int
    total_storage_tb: float
    used_storage_tb: float
    storage_utilization_pct: float
    total_network_devices: int
    total_alerts: int
    unresolved_alerts: int
    critical_alerts: int
    total_inventory: int
    active_inventory: int


class CapacityForecastPoint(BaseModel):
    month: str
    servers: int
    vms: int
    storage: float



class CapacityForecastResponse(BaseModel):
    points: List[CapacityForecastPoint] = Field(alias="forecast")
