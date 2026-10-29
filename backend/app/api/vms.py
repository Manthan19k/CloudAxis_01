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
    vm_id: str,
    vm_service: VMService = Depends(get_vm_service),
):
    if vm_id.isdigit():
        vm = await vm_service.get_vm(int(vm_id))
    else:
        vm = await vm_service.get_vm_by_vm_id(vm_id)
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
    vm_id: str,
    vm_data: VMUpdate,
    vm_service: VMService = Depends(get_vm_service),
):
    numeric_id = int(vm_id) if vm_id.isdigit() else None
    if numeric_id is None:
        existing = await vm_service.get_vm_by_vm_id(vm_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="VM not found")
    vm = await vm_service.update_vm(numeric_id, vm_data)
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
    return vm


@router.delete("/{vm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vm(
    vm_id: str,
    vm_service: VMService = Depends(get_vm_service),
):
    numeric_id = int(vm_id) if vm_id.isdigit() else None
    if numeric_id is None:
        existing = await vm_service.get_vm_by_vm_id(vm_id)
        numeric_id = existing.id if existing else None
    if numeric_id is None:
        raise HTTPException(status_code=404, detail="VM not found")
    success = await vm_service.delete_vm(numeric_id)
    if not success:
        raise HTTPException(status_code=404, detail="VM not found")
    return None


@router.get("/server/{server_id}", response_model=VMListResponse)
async def list_vms_by_server(
    server_id: str,
    skip: int = 0,
    limit: int = 100,
    vm_service: VMService = Depends(get_vm_service),
):
    numeric_id = int(server_id) if server_id.isdigit() else 0
    vms = await vm_service.list_vms_by_server(numeric_id, skip=skip, limit=limit)
    return VMListResponse(
        items=vms,
        total=len(vms),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1,
    )
