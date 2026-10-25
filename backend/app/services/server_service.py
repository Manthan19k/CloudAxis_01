from __future__ import annotations

from typing import List, Optional

from app.models.server import PhysicalServer
from app.repositories.server import ServerRepository
from app.schemas.server import ServerCreate, ServerUpdate, ServerOut


class ServerService:
    def __init__(self, server_repo: ServerRepository):
        self.server_repo = server_repo

    async def get_server(self, server_id: int) -> Optional[ServerOut]:
        server = await self.server_repo.get(server_id)
        if server:
            return ServerOut.model_validate(server)
        return None

    async def get_server_by_server_id(self, server_id: str) -> Optional[ServerOut]:
        server = await self.server_repo.get_by_server_id(server_id)
        if server:
            return ServerOut.model_validate(server)
        return None

    async def create_server(self, server_data: ServerCreate) -> ServerOut:
        server = PhysicalServer(**server_data.model_dump())
        created = await self.server_repo.create(server)
        return ServerOut.model_validate(created)

    async def update_server(self, server_id: int, server_data: ServerUpdate) -> Optional[ServerOut]:
        server = await self.server_repo.get(server_id)
        if not server:
            return None

        update_data = server_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(server, field, value)

        updated = await self.server_repo.update(server)
        return ServerOut.model_validate(updated)

    async def list_servers(self, *, skip: int = 0, limit: int = 100) -> List[ServerOut]:
        servers = await self.server_repo.list_servers(skip=skip, limit=limit)
        return [ServerOut.model_validate(server) for server in servers]

    async def delete_server(self, server_id: int) -> bool:
        server = await self.server_repo.get(server_id)
        if not server:
            return False

        await self.server_repo.delete(server)
        return True
