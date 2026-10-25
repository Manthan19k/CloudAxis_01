from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.network import NetworkDevice
from app.repositories.base import BaseRepository


class NetworkRepository(BaseRepository):
    model = NetworkDevice

    async def get_by_dev_id(self, dev_id: str) -> Optional[NetworkDevice]:
        stmt: Select = select(NetworkDevice).where(NetworkDevice.dev_id == dev_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_devices(self, *, skip: int = 0, limit: int = 100) -> List[NetworkDevice]:
        stmt = select(NetworkDevice).order_by(NetworkDevice.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
