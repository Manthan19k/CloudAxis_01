"""User and Role models with RBAC relationships."""
from __future__ import annotations

import datetime as dt
import enum
from typing import List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class RoleName(str, enum.Enum):
    ADMIN = "Admin"
    ENGINEER = "Engineer"
    MANAGER = "Manager"
    VIEWER = "Viewer"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(32), unique=True, nullable=False, index=True)
    description: Mapped[str] = Column(Text, nullable=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="role", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(120), nullable=False)
    email: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = Column(String(255), nullable=False)
    department: Mapped[str] = Column(String(64), nullable=True)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False, server_default="1")
    is_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False, server_default="0")

    role_id: Mapped[int] = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    token: Mapped[str] = Column(Text, unique=True, nullable=False, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[dt.datetime] = Column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[dt.datetime] = Column(DateTime(timezone=True), default=dt.datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")