"""Pydantic schemas for users, roles and authentication."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: Optional[str] = None


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., max_length=255)
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=200)
    role_name: str = Field(default="Engineer")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[str] = Field(default=None, max_length=255)
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    email: str
    department: Optional[str] = None
    role: RoleOut
    is_active: bool
    last_login: Optional[dt.datetime] = None


class UserSummary(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    email: str
    role: str
    department: Optional[str] = None
    is_active: bool


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str
    remember: bool = True



class MessageOut(BaseModel):
    message: str