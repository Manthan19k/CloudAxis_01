"""Pydantic schemas for health and dashboard summaries."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    status: str = "ok"
    app: str
    version: str
    environment: str
    database: str = "unknown"


class DashboardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    health_score: int = Field(..., alias="healthScore")
    total_servers: int = Field(..., alias="totalServers")
    healthy_servers: int = Field(..., alias="healthyServers")
    total_vms: int = Field(..., alias="totalVms")
    healthy_vms: int = Field(..., alias="healthyVms")
    total_datastores: int = Field(..., alias="totalDatastores")
    total_storage_tb: float = Field(..., alias="totalStorageTb")
    used_storage_tb: float = Field(..., alias="usedStorageTb")
    storage_utilization_pct: float = Field(..., alias="storageUtilizationPct")
    total_network_devices: int = Field(..., alias="totalNetworkDevices")
    total_alerts: int = Field(..., alias="totalAlerts")
    unresolved_alerts: int = Field(..., alias="unresolvedAlerts")
    critical_alerts: int = Field(..., alias="criticalAlerts")
    total_inventory: int = Field(..., alias="totalInventory")
    active_inventory: int = Field(..., alias="activeInventory")


class CapacityForecastPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    month: str
    servers: int
    vms: int
    storage: float


class CapacityForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    points: List[CapacityForecastPoint] = Field(..., alias="forecast")
