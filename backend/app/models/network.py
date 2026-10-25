"""Network device model."""
from __future__ import annotations

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import Mapped

from app.core.database import Base


class NetworkDevice(Base):
    __tablename__ = "network_devices"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    dev_id: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = Column(String(120), nullable=False, index=True)
    type: Mapped[str] = Column(String(32), nullable=False, index=True)
    vendor: Mapped[str] = Column(String(64), nullable=True)
    ip: Mapped[str] = Column(String(45), nullable=True, index=True)
    throughput_gbps: Mapped[float] = Column(Float, nullable=False, default=0.0)
    latency_ms: Mapped[float] = Column(Float, nullable=False, default=0.0)
    packet_loss: Mapped[float] = Column(Float, nullable=False, default=0.0)
    status: Mapped[str] = Column(String(16), nullable=False, default="healthy", index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NetworkDevice id={self.dev_id!r}>"