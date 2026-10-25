from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import LoginRequest, RefreshRequest, TokenPair, UserCreate, UserOut
from app.dependencies import get_user_repo

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_auth_service(user_repo = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)


def get_user_service(user_repo = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service),
) -> UserOut:
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload.get("sub")) if payload.get("sub") else None
        if not user_id:
            raise UnauthorizedError("Invalid token")
    except Exception:
        raise UnauthorizedError("Invalid token")
    
    user = await user_service.get_user(user_id)
    if not user:
        raise UnauthorizedError("User not found")
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
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
