from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.storage_service import StorageService
from app.schemas.storage import DatastoreCreate, DatastoreUpdate, DatastoreOut, DatastoreListResponse
from app.dependencies import get_storage_repo


router = APIRouter(prefix="/storage", tags=["storage"])


def get_storage_service(storage_repo = Depends(get_storage_repo)) -> StorageService:
    return StorageService(storage_repo)


@router.get("/", response_model=DatastoreListResponse)
async def list_datastores(
    skip: int = 0,
    limit: int = 100,
    storage_service: StorageService = Depends(get_storage_service),
):
    datastores = await storage_service.list_datastores(skip=skip, limit=limit)
    return DatastoreListResponse(
        items=datastores,
        total=len(datastores),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1,
    )


@router.get("/{ds_id}", response_model=DatastoreOut)
async def get_datastore(
    ds_id: int,
    storage_service: StorageService = Depends(get_storage_service),
):
    datastore = await storage_service.get_datastore(ds_id)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")
    return datastore


@router.post("/", response_model=DatastoreOut, status_code=status.HTTP_201_CREATED)
async def create_datastore(
    datastore_data: DatastoreCreate,
    storage_service: StorageService = Depends(get_storage_service),
):
    return await storage_service.create_datastore(datastore_data)


@router.put("/{ds_id}", response_model=DatastoreOut)
async def update_datastore(
    ds_id: int,
    datastore_data: DatastoreUpdate,
    storage_service: StorageService = Depends(get_storage_service),
):
    datastore = await storage_service.update_datastore(ds_id, datastore_data)
    if not datastore:
        raise HTTPException(status_code=404, detail="Datastore not found")
    return datastore


@router.delete("/{ds_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_datastore(
    ds_id: int,
    storage_service: StorageService = Depends(get_storage_service),
):
    success = await storage_service.delete_datastore(ds_id)
    if not success:
        raise HTTPException(status_code=404, detail="Datastore not found")
    return None
