from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.inventory_service import InventoryService
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryOut, InventoryListResponse
from app.dependencies import get_inventory_repo


router = APIRouter(prefix="/inventory", tags=["inventory"])


def get_inventory_service(inventory_repo = Depends(get_inventory_repo)) -> InventoryService:
    return InventoryService(inventory_repo)


@router.get("/", response_model=InventoryListResponse)
async def list_inventory(
    skip: int = 0,
    limit: int = 100,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    items = await inventory_service.list_inventory(skip=skip, limit=limit)
    return InventoryListResponse(
        items=items,
        total=len(items),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1
    )


@router.get("/{inv_id}", response_model=InventoryOut)
async def get_inventory_item(
    inv_id: str,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    if inv_id.isdigit():
        item = await inventory_service.get_inventory_item(int(inv_id))
    else:
        item = await inventory_service.get_inventory_item_by_inv_id(inv_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.post("/", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryCreate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    return await inventory_service.create_inventory_item(item_data)


@router.put("/{inv_id}", response_model=InventoryOut)
async def update_inventory_item(
    inv_id: str,
    item_data: InventoryUpdate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    numeric_id = int(inv_id) if inv_id.isdigit() else None
    if numeric_id is None:
        existing = await inventory_service.get_inventory_item_by_inv_id(inv_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    item = await inventory_service.update_inventory_item(numeric_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.delete("/{inv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    inv_id: str,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    numeric_id = int(inv_id) if inv_id.isdigit() else None
    if numeric_id is None:
        existing = await inventory_service.get_inventory_item_by_inv_id(inv_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    success = await inventory_service.delete_inventory_item(numeric_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return None


@router.get("/category/{category}", response_model=InventoryListResponse)
async def list_inventory_by_category(
    category: str,
    skip: int = 0,
    limit: int = 100,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    items = await inventory_service.list_inventory_by_category(category, skip=skip, limit=limit)
    return InventoryListResponse(
        items=items,
        total=len(items),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1,
    )
