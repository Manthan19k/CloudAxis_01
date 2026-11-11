from __future__ import annotations

from typing import AsyncGenerator, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, engine, async_session_maker, get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.repositories.alert import AlertRepository
from app.repositories.inventory import InventoryRepository
from app.repositories.monitoring import MonitoringRepository
from app.repositories.network import NetworkRepository
from app.repositories.server import ServerRepository
from app.repositories.storage import StorageRepository
from app.repositories.user import UserRepository
from app.repositories.vm import VMRepository
from app.schemas.user import UserOut
from app.services.user_service import UserService

security = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> UserOut:
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Missing authentication token")
    try:
        payload = decode_token(credentials.credentials)
        if not payload or payload.get("type") != "access":
            raise UnauthorizedError("Invalid or expired token")
        user_id = int(payload.get("sub")) if payload.get("sub") else None
        if not user_id:
            raise UnauthorizedError("Invalid token")
    except UnauthorizedError:
        raise
    except Exception:
        raise UnauthorizedError("Invalid token")

    user = await user_service.get_user(user_id)
    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("Account is inactive or disabled")
    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> Optional[UserOut]:
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if not payload or payload.get("type") != "access":
            return None
        user_id = int(payload.get("sub")) if payload.get("sub") else None
        if not user_id:
            return None
        user = await user_service.get_user(user_id)
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None


def require_roles(*allowed_roles: str):
    """Dependency factory that validates the authenticated caller has one of the allowed roles."""
    norm_roles = {r.strip().lower() for r in allowed_roles}

    async def role_checker(
        current_user: UserOut = Depends(get_current_user),
    ) -> UserOut:
        user_role = (current_user.role or "").strip().lower()
        if user_role not in norm_roles:
            raise ForbiddenError(f"Role '{current_user.role}' does not have sufficient permissions")
        return current_user

    return role_checker


# Convenient RBAC presets
require_admin = require_roles("admin")
require_engineer_or_admin = require_roles("admin", "engineer")
require_operational_write = require_roles("admin", "engineer", "manager")
require_authenticated = get_current_user


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
