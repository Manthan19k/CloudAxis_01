"""Physical server model."""
from __future__ import annotations

import enum
from typing import List

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class ServerStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class PhysicalServer(Base):
    __tablename__ = "physical_servers"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    server_id: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = Column(String(120), nullable=False, index=True)
    ip: Mapped[str] = Column(String(45), nullable=False, index=True)
    location: Mapped[str] = Column(String(64), nullable=False, index=True)
    rack: Mapped[str] = Column(String(32), nullable=True)
    os: Mapped[str] = Column(String(64), nullable=True)
    cpu: Mapped[float] = Column(Float, nullable=False, default=0.0)
    memory: Mapped[float] = Column(Float, nullable=False, default=0.0)
    storage: Mapped[float] = Column(Float, nullable=False, default=0.0)
    temperature: Mapped[float] = Column(Float, nullable=False, default=0.0)
    status: Mapped[str] = Column(String(16), nullable=False, default="healthy", index=True)
    owner: Mapped[str] = Column(String(120), nullable=True)
    department: Mapped[str] = Column(String(64), nullable=True)
    vm_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    uptime_days: Mapped[int] = Column(Integer, nullable=False, default=0)

    vms: Mapped[List["VirtualMachine"]] = relationship("VirtualMachine", back_populates="host_server")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PhysicalServer id={self.server_id!r} status={self.status!r}>"