"""Alert model."""
from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    severity: Mapped[str] = Column(String(16), nullable=False, index=True)
    title: Mapped[str] = Column(Text, nullable=False)
    source: Mapped[str] = Column(String(120), nullable=True, index=True)
    triggered_at: Mapped[dt.datetime] = Column(DateTime(timezone=True), nullable=False, index=True)
    acknowledged: Mapped[bool] = Column(Boolean, default=False, nullable=False, server_default="0")
    resolved: Mapped[bool] = Column(Boolean, default=False, nullable=False, server_default="0")
    assignee: Mapped[str] = Column(String(120), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Alert id={self.alert_id!r} severity={self.severity!r}>"