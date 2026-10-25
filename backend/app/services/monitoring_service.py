from __future__ import annotations

from typing import List, Optional

from app.models.monitoring import MetricSample
from app.repositories.monitoring import MonitoringRepository
from app.schemas.monitoring import MetricSampleCreate, MetricSampleOut


class MonitoringService:
    def __init__(self, monitoring_repo: MonitoringRepository):
        self.monitoring_repo = monitoring_repo

    async def create_metric(self, metric_data: MetricSampleCreate) -> MetricSampleOut:
        metric = MetricSample(**metric_data.model_dump())
        created = await self.monitoring_repo.create(metric)
        return MetricSampleOut.model_validate(created)

    async def list_metrics_by_device(self, device_id: str, *, skip: int = 0, limit: int = 100) -> List[MetricSampleOut]:
        metrics = await self.monitoring_repo.list_by_device(device_id, skip=skip, limit=limit)
        return [MetricSampleOut.model_validate(m) for m in metrics]

    async def list_recent_metrics(self, *, hours: int = 24, skip: int = 0, limit: int = 100) -> List[MetricSampleOut]:
        metrics = await self.monitoring_repo.list_recent(hours=hours, skip=skip, limit=limit)
        return [MetricSampleOut.model_validate(m) for m in metrics]
