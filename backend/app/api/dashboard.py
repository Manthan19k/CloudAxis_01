from __future__ import annotations

from fastapi import APIRouter, Depends
from app.services.dashboard_service import DashboardService
from app.schemas.health import DashboardSummary, CapacityForecastResponse
from app.dependencies import (
    get_server_repo, get_vm_repo, get_storage_repo, get_network_repo,
    get_alert_repo, get_inventory_repo, get_monitoring_repo
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_service(
    server_repo = Depends(get_server_repo),
    vm_repo = Depends(get_vm_repo),
    storage_repo = Depends(get_storage_repo),
    network_repo = Depends(get_network_repo),
    alert_repo = Depends(get_alert_repo),
    inventory_repo = Depends(get_inventory_repo),
    monitoring_repo = Depends(get_monitoring_repo),
) -> DashboardService:
    return DashboardService(
        server_repo=server_repo,
        vm_repo=vm_repo,
        storage_repo=storage_repo,
        network_repo=network_repo,
        alert_repo=alert_repo,
        inventory_repo=inventory_repo,
        monitoring_repo=monitoring_repo,
    )


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    return await dashboard_service.get_dashboard_summary()


@router.get("/forecast", response_model=CapacityForecastResponse)
async def get_capacity_forecast(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    return await dashboard_service.get_capacity_forecast()
