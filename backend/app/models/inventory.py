"""Asset inventory model."""
from __future__ import annotations

import datetime as dt
import enum

from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped

from app.core.database import Base


class InventoryCategory(str, enum.Enum):
    SERVER = "Server"
    SWITCH = "Switch"
    ROUTER = "Router"
    FIREWALL = "Firewall"
    STORAGE = "Storage"
    LICENSE = "License"
    SOFTWARE = "Software"


class InventoryStatus(str, enum.Enum):
    ACTIVE = "Active"
    RETIRED = "Retired"
    IN_STOCK = "In Stock"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    inv_id: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    category: Mapped[str] = Column(String(32), nullable=False, index=True)
    name: Mapped[str] = Column(String(120), nullable=False, index=True)
    vendor: Mapped[str] = Column(String(64), nullable=True)
    serial: Mapped[str] = Column(String(64), nullable=True, index=True)
    purchased_at: Mapped[dt.datetime] = Column(DateTime, nullable=True)
    warranty_until: Mapped[dt.datetime] = Column(DateTime, nullable=True)
    status: Mapped[str] = Column(String(16), nullable=False, default="Active", index=True)

    @property
    def purchased(self) -> Optional[str]:
        if self.purchased_at is not None:
            return self.purchased_at.strftime("%Y-%m-%d") if hasattr(self.purchased_at, "strftime") else str(self.purchased_at)[:10]
        return None

    @property
    def warranty(self) -> Optional[str]:
        if self.warranty_until is not None:
            return self.warranty_until.strftime("%Y-%m-%d") if hasattr(self.warranty_until, "strftime") else str(self.warranty_until)[:10]
        return None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InventoryItem id={self.inv_id!r} category={self.category!r}>"