from __future__ import annotations

import datetime as dt
from typing import List, Optional

from app.models.alert import Alert
from app.models.inventory import InventoryItem
from app.models.monitoring import MetricSample
from app.models.network import NetworkDevice
from app.models.server import PhysicalServer
from app.models.storage import Datastore
from app.models.vm import VirtualMachine
from app.repositories.alert import AlertRepository
from app.repositories.inventory import InventoryRepository
from app.repositories.monitoring import MonitoringRepository
from app.repositories.network import NetworkRepository
from app.repositories.server import ServerRepository
from app.repositories.storage import StorageRepository
from app.repositories.vm import VMRepository
from app.schemas.health import DashboardSummary, CapacityForecastPoint, CapacityForecastResponse


class DashboardService:
    def __init__(
        self,
        server_repo: ServerRepository,
        vm_repo: VMRepository,
        storage_repo: StorageRepository,
        network_repo: NetworkRepository,
        alert_repo: AlertRepository,
        inventory_repo: InventoryRepository,
        monitoring_repo: MonitoringRepository,
    ):
        self.server_repo = server_repo
        self.vm_repo = vm_repo
        self.storage_repo = storage_repo
        self.network_repo = network_repo
        self.alert_repo = alert_repo
        self.inventory_repo = inventory_repo
        self.monitoring_repo = monitoring_repo

    async def get_dashboard_summary(self) -> DashboardSummary:
        # Get counts
        servers = await self.server_repo.list_servers()
        vms = await self.vm_repo.list_vms()
        storages = await self.storage_repo.list_datastores()
        networks = await self.network_repo.list_devices()
        alerts = await self.alert_repo.list_alerts()
        inventory_items = await self.inventory_repo.list_inventory()

        # Count by status
        healthy_servers = sum(1 for s in servers if s.status == "healthy")
        warning_servers = sum(1 for s in servers if s.status == "warning")
        critical_servers = sum(1 for s in servers if s.status == "critical")
        offline_servers = sum(1 for s in servers if s.status == "offline")

        healthy_vms = sum(1 for v in vms if v.status == "healthy")
        warning_vms = sum(1 for v in vms if v.status == "warning")
        critical_vms = sum(1 for v in vms if v.status == "critical")
        offline_vms = sum(1 for v in vms if v.status == "offline")

        # Storage utilization (simplified)
        total_storage_capacity = sum(s.capacity_tb for s in storages)
        total_storage_used = sum(s.used_tb for s in storages)
        storage_utilization_percent = (total_storage_used / total_storage_capacity * 100) if total_storage_capacity > 0 else 0

        # Network utilization (average)
        # NetworkDevice has throughput_gbps, latency_ms, packet_loss (no utilization_percent)
        # We can calculate a simple score or omit it if not in DashboardSummary
        critical_alerts = sum(1 for a in alerts if a.severity == "critical")

        warning_alerts = sum(1 for a in alerts if a.severity == "warning")
        info_alerts = sum(1 for a in alerts if a.severity == "info")

        return DashboardSummary(
            health_score=95, # Mocked
            total_servers=len(servers),
            healthy_servers=healthy_servers,
            total_vms=len(vms),
            healthy_vms=healthy_vms,
            total_datastores=len(storages),
            total_storage_tb=total_storage_capacity,
            used_storage_tb=total_storage_used,
            storage_utilization_pct=round(storage_utilization_percent, 2),
            total_network_devices=len(networks),
            total_alerts=len(alerts),
            unresolved_alerts=len([a for a in alerts if not a.resolved]),
            critical_alerts=critical_alerts,
            total_inventory=len(inventory_items),
            active_inventory=len([i for i in inventory_items if i.status == "Active"]),
        )

    async def get_capacity_forecast(self) -> CapacityForecastResponse:
        # Generate mock forecast data for next 12 months
        forecast_points = []
        base_date = dt.datetime.utcnow()
        
        for i in range(12):
            point_date = base_date + dt.timedelta(days=30*i)
            # Simple linear growth forecast
            forecast_points.append(CapacityForecastPoint(
                month=point_date.strftime("%Y-%m"),
                servers=50 + (i * 5),
                vms=10 + (i * 2),
                storage=1000.0 + (i * 50.0),
            ))

        return CapacityForecastResponse(forecast=forecast_points)

