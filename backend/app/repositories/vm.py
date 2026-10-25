from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vm import VirtualMachine
from app.repositories.base import BaseRepository


class VMRepository(BaseRepository):
    model = VirtualMachine

    async def get_by_vm_id(self, vm_id: str) -> Optional[VirtualMachine]:
        stmt: Select = select(VirtualMachine).where(VirtualMachine.vm_id == vm_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_vms(self, *, skip: int = 0, limit: int = 100) -> List[VirtualMachine]:
        stmt = select(VirtualMachine).order_by(VirtualMachine.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_server(self, server_id: int, *, skip: int = 0, limit: int = 100) -> List[VirtualMachine]:
        stmt = (
            select(VirtualMachine)
            .where(VirtualMachine.physical_server_id == server_id)
            .order_by(VirtualMachine.id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
