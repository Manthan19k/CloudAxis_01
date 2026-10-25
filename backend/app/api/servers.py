from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.server_service import ServerService
from app.schemas.server import ServerCreate, ServerUpdate, ServerOut, ServerListResponse
from app.dependencies import get_server_repo


router = APIRouter(prefix="/servers", tags=["servers"])


def get_server_service(server_repo = Depends(get_server_repo)) -> ServerService:
    return ServerService(server_repo)


@router.get("/", response_model=ServerListResponse)
async def list_servers(
    skip: int = 0,
    limit: int = 100,
    server_service: ServerService = Depends(get_server_service),
):
    servers = await server_service.list_servers(skip=skip, limit=limit)
    return ServerListResponse(
        items=servers,
        total=len(servers),
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=1
    )


@router.get("/{server_id}", response_model=ServerOut)
async def get_server(
    server_id: int,
    server_service: ServerService = Depends(get_server_service),
):
    server = await server_service.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("/", response_model=ServerOut, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: ServerCreate,
    server_service: ServerService = Depends(get_server_service),
):
    return await server_service.create_server(server_data)


@router.put("/{server_id}", response_model=ServerOut)
async def update_server(
    server_id: int,
    server_data: ServerUpdate,
    server_service: ServerService = Depends(get_server_service),
):
    server = await server_service.update_server(server_id, server_data)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    server_service: ServerService = Depends(get_server_service),
):
    success = await server_service.delete_server(server_id)
    if not success:
        raise HTTPException(status_code=404, detail="Server not found")
    return None
