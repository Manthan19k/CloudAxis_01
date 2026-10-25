from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring import MetricSample
from app.repositories.base import BaseRepository


class MonitoringRepository(BaseRepository):
    model = MetricSample

    async def list_by_device(self, device_id: str, *, skip: int = 0, limit: int = 100) -> List[MetricSample]:
        stmt: Select = select(MetricSample).where(MetricSample.source == device_id)
        stmt = stmt.order_by(MetricSample.recorded_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(self, *, hours: int = 24, skip: int = 0, limit: int = 100) -> List[MetricSample]:
        from datetime import datetime, timedelta
        
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(MetricSample)
            .where(MetricSample.recorded_at >= since)
            .order_by(MetricSample.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
