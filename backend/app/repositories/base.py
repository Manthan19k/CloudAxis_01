from __future__ import annotations

from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError


class BaseRepository:
    """Generic CRUD helper operating on a SQLAlchemy model."""

    model = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id_: int):
        return await self.session.get(self.model, id_)

    async def get_by(self, **kwargs):
        stmt: Select = select(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, *, skip: int = 0, limit: int = 100, order_by=None):
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj):
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj):
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj):
        await self.session.delete(obj)
        await self.session.flush()

    async def count(self, **kwargs) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
