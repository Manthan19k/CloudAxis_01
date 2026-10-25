from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.storage import Datastore
from app.repositories.base import BaseRepository


class StorageRepository(BaseRepository):
    model = Datastore

    async def get_by_ds_id(self, ds_id: str) -> Optional[Datastore]:
        stmt: Select = select(Datastore).where(Datastore.ds_id == ds_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_datastores(self, *, skip: int = 0, limit: int = 100) -> List[Datastore]:
        stmt = select(Datastore).order_by(Datastore.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
