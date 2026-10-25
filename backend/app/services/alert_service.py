from __future__ import annotations

from typing import List, Optional

from app.models.alert import Alert
from app.repositories.alert import AlertRepository
from app.schemas.alert import AlertCreate, AlertUpdate, AlertOut


class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    async def get_alert(self, alert_id: int) -> Optional[AlertOut]:
        alert = await self.alert_repo.get(alert_id)
        if alert:
            return AlertOut.model_validate(alert)
        return None

    async def get_alert_by_alert_id(self, alert_id: str) -> Optional[AlertOut]:
        alert = await self.alert_repo.get_by_alert_id(alert_id)
        if alert:
            return AlertOut.model_validate(alert)
        return None

    async def create_alert(self, alert_data: AlertCreate) -> AlertOut:
        alert = Alert(**alert_data.model_dump())
        created = await self.alert_repo.create(alert)
        return AlertOut.model_validate(created)

    async def update_alert(self, alert_id: int, alert_data: AlertUpdate) -> Optional[AlertOut]:
        alert = await self.alert_repo.get(alert_id)
        if not alert:
            return None

        update_data = alert_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(alert, field, value)

        updated = await self.alert_repo.update(alert)
        return AlertOut.model_validate(updated)

    async def list_alerts(self, *, skip: int = 0, limit: int = 100) -> List[AlertOut]:
        alerts = await self.alert_repo.list_alerts(skip=skip, limit=limit)
        return [AlertOut.model_validate(alert) for alert in alerts]

    async def list_alerts_by_severity(self, severity: str, *, skip: int = 0, limit: int = 100) -> List[AlertOut]:
        alerts = await self.alert_repo.list_by_severity(severity, skip=skip, limit=limit)
        return [AlertOut.model_validate(alert) for alert in alerts]

    async def delete_alert(self, alert_id: int) -> bool:
        alert = await self.alert_repo.get(alert_id)
        if not alert:
            return False

        await self.alert_repo.delete(alert)
        return True
