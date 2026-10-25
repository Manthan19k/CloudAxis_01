from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository):
    model = Alert

    async def get_by_alert_id(self, alert_id: str) -> Optional[Alert]:
        stmt: Select = select(Alert).where(Alert.alert_id == alert_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_alerts(self, *, skip: int = 0, limit: int = 100) -> List[Alert]:
        stmt = select(Alert).order_by(Alert.triggered_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_severity(self, severity: str, *, skip: int = 0, limit: int = 100) -> List[Alert]:
        stmt = (
            select(Alert)
            .where(Alert.severity == severity)
            .order_by(Alert.triggered_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
