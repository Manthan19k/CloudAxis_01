from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.monitoring_service import MonitoringService
from app.schemas.monitoring import MetricSampleCreate, MetricSampleOut
from app.dependencies import get_monitoring_repo


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def get_monitoring_service(monitoring_repo = Depends(get_monitoring_repo)) -> MonitoringService:
    return MonitoringService(monitoring_repo)


@router.post("/", response_model=MetricSampleOut, status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric_data: MetricSampleCreate,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    return await monitoring_service.create_metric(metric_data)


@router.get("/device/{device_id}", response_model=List[MetricSampleOut])
async def list_metrics_by_device(
    device_id: str,
    skip: int = 0,
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    metrics = await monitoring_service.list_metrics_by_device(device_id, skip=skip, limit=limit)
    return metrics


@router.get("/recent", response_model=List[MetricSampleOut])
async def list_recent_metrics(
    hours: int = 24,
    skip: int = 0,
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
):
    metrics = await monitoring_service.list_recent_metrics(hours=hours, skip=skip, limit=limit)
    return metrics
