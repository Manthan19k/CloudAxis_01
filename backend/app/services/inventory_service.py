from __future__ import annotations

from typing import List, Optional

from app.models.inventory import InventoryItem
from app.repositories.inventory import InventoryRepository
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryOut


class InventoryService:
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo

    async def get_inventory_item(self, inv_id: int) -> Optional[InventoryOut]:
        item = await self.inventory_repo.get(inv_id)
        if item:
            return InventoryOut.model_validate(item)
        return None

    async def get_inventory_item_by_inv_id(self, inv_id: str) -> Optional[InventoryOut]:
        item = await self.inventory_repo.get_by_inv_id(inv_id)
        if item:
            return InventoryOut.model_validate(item)
        return None

    async def create_inventory_item(self, item_data: InventoryCreate) -> InventoryOut:
        item = InventoryItem(**item_data.model_dump())
        created = await self.inventory_repo.create(item)
        return InventoryOut.model_validate(created)

    async def update_inventory_item(self, inv_id: int, item_data: InventoryUpdate) -> Optional[InventoryOut]:
        item = await self.inventory_repo.get(inv_id)
        if not item:
            return None

        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        updated = await self.inventory_repo.update(item)
        return InventoryOut.model_validate(updated)

    async def list_inventory(self, *, skip: int = 0, limit: int = 100) -> List[InventoryOut]:
        items = await self.inventory_repo.list_inventory(skip=skip, limit=limit)
        return [InventoryOut.model_validate(item) for item in items]

    async def list_inventory_by_category(self, category: str, *, skip: int = 0, limit: int = 100) -> List[InventoryOut]:
        items = await self.inventory_repo.list_by_category(category, skip=skip, limit=limit)
        return [InventoryOut.model_validate(item) for item in items]

    async def delete_inventory_item(self, inv_id: int) -> bool:
        item = await self.inventory_repo.get(inv_id)
        if not item:
            return False

        await self.inventory_repo.delete(item)
        return True
