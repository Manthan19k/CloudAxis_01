from __future__ import annotations

from typing import List, Optional

from app.models.network import NetworkDevice
from app.repositories.network import NetworkRepository
from app.schemas.network import NetworkDeviceCreate, NetworkDeviceUpdate, NetworkDeviceOut


class NetworkService:
    def __init__(self, network_repo: NetworkRepository):
        self.network_repo = network_repo

    async def get_device(self, dev_id: int) -> Optional[NetworkDeviceOut]:
        device = await self.network_repo.get(dev_id)
        if device:
            return NetworkDeviceOut.model_validate(device)
        return None

    async def get_device_by_dev_id(self, dev_id: str) -> Optional[NetworkDeviceOut]:
        device = await self.network_repo.get_by_dev_id(dev_id)
        if device:
            return NetworkDeviceOut.model_validate(device)
        return None

    async def create_device(self, device_data: NetworkDeviceCreate) -> NetworkDeviceOut:
        device = NetworkDevice(**device_data.model_dump())
        created = await self.network_repo.create(device)
        return NetworkDeviceOut.model_validate(created)

    async def update_device(self, dev_id: int, device_data: NetworkDeviceUpdate) -> Optional[NetworkDeviceOut]:
        device = await self.network_repo.get(dev_id)
        if not device:
            return None

        update_data = device_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)

        updated = await self.network_repo.update(device)
        return NetworkDeviceOut.model_validate(updated)

    async def list_devices(self, *, skip: int = 0, limit: int = 100) -> List[NetworkDeviceOut]:
        devices = await self.network_repo.list_devices(skip=skip, limit=limit)
        return [NetworkDeviceOut.model_validate(d) for d in devices]

    async def delete_device(self, dev_id: int) -> bool:
        device = await self.network_repo.get(dev_id)
        if not device:
            return False

        await self.network_repo.delete(device)
        return True
