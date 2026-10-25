"""Monitoring metric samples."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped

from app.core.database import Base


class MetricSample(Base):
    __tablename__ = "metric_samples"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    source: Mapped[str] = Column(String(120), nullable=False, index=True)
    metric: Mapped[str] = Column(String(64), nullable=False, index=True)
    value: Mapped[float] = Column(Float, nullable=False)
    unit: Mapped[str] = Column(String(16), nullable=True)
    recorded_at: Mapped[dt.datetime] = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MetricSample source={self.source!r} metric={self.metric!r} value={self.value}>"