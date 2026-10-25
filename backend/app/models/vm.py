"""Virtual machine model."""
from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    vm_id: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = Column(String(120), nullable=False, index=True)
    host_id: Mapped[int] = Column(Integer, ForeignKey("physical_servers.id", ondelete="SET NULL"), nullable=True, index=True)
    host_name: Mapped[str] = Column(String(120), nullable=True)
    os: Mapped[str] = Column(String(64), nullable=True)
    v_cpu: Mapped[int] = Column(Integer, nullable=False, default=2)
    memory_gb: Mapped[int] = Column(Integer, nullable=False, default=4)
    disk_gb: Mapped[int] = Column(Integer, nullable=False, default=40)
    cpu: Mapped[float] = Column(Float, nullable=False, default=0.0)
    memory: Mapped[float] = Column(Float, nullable=False, default=0.0)
    status: Mapped[str] = Column(String(16), nullable=False, default="healthy", index=True)
    ip: Mapped[str] = Column(String(45), nullable=True)
    owner: Mapped[str] = Column(String(120), nullable=True)
    department: Mapped[str] = Column(String(64), nullable=True)
    snapshots: Mapped[int] = Column(Integer, nullable=False, default=0)

    host_server: Mapped["PhysicalServer"] = relationship("PhysicalServer", back_populates="vms")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<VirtualMachine id={self.vm_id!r} status={self.status!r}>"