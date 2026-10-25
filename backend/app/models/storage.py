"""Datastore / storage model."""
from __future__ import annotations

import enum

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import Mapped

from app.core.database import Base


class DatastoreType(str, enum.Enum):
    SSD = "SSD"
    NVMe = "NVMe"
    HDD = "HDD"
    HYBRID = "Hybrid"


class DatastoreStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class Datastore(Base):
    __tablename__ = "datastores"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    ds_id: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = Column(String(120), nullable=False, index=True)
    type: Mapped[str] = Column(String(16), nullable=False, index=True)
    capacity_tb: Mapped[float] = Column(Float, nullable=False, default=0.0)
    used_tb: Mapped[float] = Column(Float, nullable=False, default=0.0)
    status: Mapped[str] = Column(String(16), nullable=False, default="healthy", index=True)
    location: Mapped[str] = Column(String(64), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Datastore id={self.ds_id!r}>"