from __future__ import annotations

from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.server import ServerRepository
from app.repositories.vm import VMRepository
from app.repositories.storage import StorageRepository
from app.repositories.network import NetworkRepository
from app.repositories.alert import AlertRepository
from app.repositories.monitoring import MonitoringRepository
from app.repositories.inventory import InventoryRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ServerRepository",
    "VMRepository",
    "StorageRepository",
    "NetworkRepository",
    "AlertRepository",
    "MonitoringRepository",
    "InventoryRepository",
]
