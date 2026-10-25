from __future__ import annotations

from typing import List, Optional

from app.models.vm import VirtualMachine
from app.repositories.vm import VMRepository
from app.schemas.vm import VMCreate, VMUpdate, VMOut


class VMService:
    def __init__(self, vm_repo: VMRepository):
        self.vm_repo = vm_repo

    async def get_vm(self, vm_id: int) -> Optional[VMOut]:
        vm = await self.vm_repo.get(vm_id)
        if vm:
            return VMOut.model_validate(vm)
        return None

    async def get_vm_by_vm_id(self, vm_id: str) -> Optional[VMOut]:
        vm = await self.vm_repo.get_by_vm_id(vm_id)
        if vm:
            return VMOut.model_validate(vm)
        return None

    async def create_vm(self, vm_data: VMCreate) -> VMOut:
        vm = VirtualMachine(**vm_data.model_dump())
        created = await self.vm_repo.create(vm)
        return VMOut.model_validate(created)

    async def update_vm(self, vm_id: int, vm_data: VMUpdate) -> Optional[VMOut]:
        vm = await self.vm_repo.get(vm_id)
        if not vm:
            return None

        update_data = vm_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vm, field, value)

        updated = await self.vm_repo.update(vm)
        return VMOut.model_validate(updated)

    async def list_vms(self, *, skip: int = 0, limit: int = 100) -> List[VMOut]:
        vms = await self.vm_repo.list_vms(skip=skip, limit=limit)
        return [VMOut.model_validate(vm) for vm in vms]

    async def list_vms_by_server(self, server_id: int, *, skip: int = 0, limit: int = 100) -> List[VMOut]:
        vms = await self.vm_repo.list_by_server(server_id, skip=skip, limit=limit)
        return [VMOut.model_validate(vm) for vm in vms]

    async def delete_vm(self, vm_id: int) -> bool:
        vm = await self.vm_repo.get(vm_id)
        if not vm:
            return False

        await self.vm_repo.delete(vm)
        return True
