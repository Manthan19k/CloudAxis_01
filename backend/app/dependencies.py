from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, engine, async_session_maker, get_db
from app.repositories.alert import AlertRepository
from app.repositories.inventory import InventoryRepository
from app.repositories.monitoring import MonitoringRepository
from app.repositories.network import NetworkRepository
from app.repositories.server import ServerRepository
from app.repositories.storage import StorageRepository
from app.repositories.user import UserRepository
from app.repositories.vm import VMRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_server_repo(session: AsyncSession = Depends(get_db_session)) -> ServerRepository:
    return ServerRepository(session)


def get_vm_repo(session: AsyncSession = Depends(get_db_session)) -> VMRepository:
    return VMRepository(session)


def get_storage_repo(session: AsyncSession = Depends(get_db_session)) -> StorageRepository:
    return StorageRepository(session)


def get_network_repo(session: AsyncSession = Depends(get_db_session)) -> NetworkRepository:
    return NetworkRepository(session)


def get_alert_repo(session: AsyncSession = Depends(get_db_session)) -> AlertRepository:
    return AlertRepository(session)


def get_monitoring_repo(session: AsyncSession = Depends(get_db_session)) -> MonitoringRepository:
    return MonitoringRepository(session)


def get_inventory_repo(session: AsyncSession = Depends(get_db_session)) -> InventoryRepository:
    return InventoryRepository(session)
