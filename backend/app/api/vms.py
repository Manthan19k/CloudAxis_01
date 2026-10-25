from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.vm_service import VMService
from app.schemas.vm import VMCreate, VMUpdate, VMOut, VMListResponse
from app.dependencies import get_vm_repo


router = APIRouter(prefix="/vms", tags=["vms"])


def get_vm_service(vm_repo = Depends(get_vm_repo)) -> VMService:
    return VMService(vm_repo)


@router.get("/", response_model=VMListResponse)
async def list_vms(
    skip: int = 0,
    limit: int = 100,
    vm_service: VMService = Depends(get_vm_service),
):
    vms = await vm_service.list_vms(skip=skip, limit=limit)
    return VMListResponse(
        items=vms,
        total=len(vms),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1,
    )


@router.get("/{vm_id}", response_model=VMOut)
async def get_vm(
    vm_id: int,
    vm_service: VMService = Depends(get_vm_service),
):
    vm = await vm_service.get_vm(vm_id)
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
    return vm


@router.post("/", response_model=VMOut, status_code=status.HTTP_201_CREATED)
async def create_vm(
    vm_data: VMCreate,
    vm_service: VMService = Depends(get_vm_service),
):
    return await vm_service.create_vm(vm_data)


@router.put("/{vm_id}", response_model=VMOut)
async def update_vm(
    vm_id: int,
    vm_data: VMUpdate,
    vm_service: VMService = Depends(get_vm_service),
):
    vm = await vm_service.update_vm(vm_id, vm_data)
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
    return vm


@router.delete("/{vm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vm(
    vm_id: int,
    vm_service: VMService = Depends(get_vm_service),
):
    success = await vm_service.delete_vm(vm_id)
    if not success:
        raise HTTPException(status_code=404, detail="VM not found")
    return None


@router.get("/server/{server_id}", response_model=VMListResponse)
async def list_vms_by_server(
    server_id: int,
    skip: int = 0,
    limit: int = 100,
    vm_service: VMService = Depends(get_vm_service),
):
    vms = await vm_service.list_vms_by_server(server_id, skip=skip, limit=limit)
    return VMListResponse(
        items=vms,
        total=len(vms),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1,
    )
