"""Pydantic schemas for users, roles and authentication."""
from __future__ import annotations

import datetime as dt
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    name: str
    description: Optional[str] = None


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., max_length=255)
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=200)
    role_name: str = Field(default="engineer", alias="roleName")


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[str] = Field(default=None, max_length=255)
    department: Optional[str] = None
    is_active: Optional[bool] = Field(default=None, alias="isActive")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    name: str
    email: str
    department: Optional[str] = None
    role: str
    is_active: bool = Field(..., alias="isActive")
    last_login: Optional[dt.datetime] = Field(default=None, alias="lastLogin")

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v: Any) -> str:
        if hasattr(v, "name"):
            return str(v.name).lower()
        if isinstance(v, dict) and "name" in v:
            return str(v["name"]).lower()
        if isinstance(v, str):
            return v.lower()
        return "viewer"

    @computed_field(alias="active")
    def active_alias(self) -> bool:
        return self.is_active


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    name: str
    email: str
    role: str
    department: Optional[str] = None
    is_active: bool = Field(..., alias="isActive")


class TokenPair(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class RefreshRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    refresh_token: str = Field(..., alias="refreshToken")


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    email: Optional[str] = None
    username: Optional[str] = None
    password: str
    remember: bool = True


class MessageOut(BaseModel):
    message: str
