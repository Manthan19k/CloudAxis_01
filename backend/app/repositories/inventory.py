from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository):
    model = InventoryItem

    async def get_by_inv_id(self, inv_id: str) -> Optional[InventoryItem]:
        stmt: Select = select(InventoryItem).where(InventoryItem.inv_id == inv_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_inventory(self, *, skip: int = 0, limit: int = 100) -> List[InventoryItem]:
        stmt = select(InventoryItem).order_by(InventoryItem.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_category(self, category: str, *, skip: int = 0, limit: int = 100) -> List[InventoryItem]:
        stmt = (
            select(InventoryItem)
            .where(InventoryItem.category == category)
            .order_by(InventoryItem.id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
