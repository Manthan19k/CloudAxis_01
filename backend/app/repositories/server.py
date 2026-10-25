from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.server import PhysicalServer
from app.repositories.base import BaseRepository


class ServerRepository(BaseRepository):
    model = PhysicalServer

    async def get_by_server_id(self, server_id: str) -> Optional[PhysicalServer]:
        stmt: Select = select(PhysicalServer).where(PhysicalServer.server_id == server_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_servers(self, *, skip: int = 0, limit: int = 100) -> List[PhysicalServer]:
        stmt = select(PhysicalServer).order_by(PhysicalServer.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
