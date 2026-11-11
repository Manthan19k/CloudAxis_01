from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.services.auth_service import AuthService
from app.schemas.user import LoginRequest, RefreshRequest, TokenPair, UserCreate, UserOut
from app.dependencies import (
    get_user_repo,
    get_user_service,
    get_current_user,
    get_optional_current_user,
    security,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(user_repo = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenPair)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.authenticate_user(login_data)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    refresh_data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_token(refresh_data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout_user(refresh_data.refresh_token)
    return None


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: UserOut = Depends(get_current_user),
):
    return current_user
