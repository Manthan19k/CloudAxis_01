from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.network_service import NetworkService
from app.schemas.network import NetworkDeviceCreate, NetworkDeviceUpdate, NetworkDeviceOut, NetworkDeviceListResponse
from app.schemas.user import UserOut
from app.dependencies import (
    get_network_repo,
    require_authenticated,
    require_engineer_or_admin,
)


router = APIRouter(prefix="/network", tags=["network"])


def get_network_service(network_repo = Depends(get_network_repo)) -> NetworkService:
    return NetworkService(network_repo)


@router.get("/", response_model=NetworkDeviceListResponse)
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    network_service: NetworkService = Depends(get_network_service),
    current_user: UserOut = Depends(require_authenticated),
):
    devices = await network_service.list_devices(skip=skip, limit=limit)
    return NetworkDeviceListResponse(
        items=devices,
        total=len(devices),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1,
    )


@router.get("/{dev_id}", response_model=NetworkDeviceOut)
async def get_device(
    dev_id: str,
    network_service: NetworkService = Depends(get_network_service),
    current_user: UserOut = Depends(require_authenticated),
):
    if dev_id.isdigit():
        device = await network_service.get_device(int(dev_id))
    else:
        device = await network_service.get_device_by_dev_id(dev_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/", response_model=NetworkDeviceOut, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: NetworkDeviceCreate,
    network_service: NetworkService = Depends(get_network_service),
    current_user: UserOut = Depends(require_engineer_or_admin),
):
    return await network_service.create_device(device_data)


@router.put("/{dev_id}", response_model=NetworkDeviceOut)
async def update_device(
    dev_id: str,
    device_data: NetworkDeviceUpdate,
    network_service: NetworkService = Depends(get_network_service),
    current_user: UserOut = Depends(require_engineer_or_admin),
):
    numeric_id = int(dev_id) if dev_id.isdigit() else None
    if numeric_id is None:
        existing = await network_service.get_device_by_dev_id(dev_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="Device not found")
    device = await network_service.update_device(numeric_id, device_data)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{dev_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    dev_id: str,
    network_service: NetworkService = Depends(get_network_service),
    current_user: UserOut = Depends(require_engineer_or_admin),
):
    numeric_id = int(dev_id) if dev_id.isdigit() else None
    if numeric_id is None:
        existing = await network_service.get_device_by_dev_id(dev_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="Device not found")
    success = await network_service.delete_device(numeric_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return None
