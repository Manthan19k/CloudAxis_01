from __future__ import annotations

import datetime as dt
from typing import Optional

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.config import get_settings
from app.models.user import RefreshToken, Role, User
from app.repositories.user import UserRepository
from app.schemas.user import LoginRequest, RefreshRequest, TokenPair, UserCreate, UserOut

settings = get_settings()


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_data: UserCreate) -> TokenPair:
        # Check if user already exists
        clean_email = user_data.email.strip().lower()
        existing = await self.user_repo.get_by_email(clean_email)
        if existing:
            raise ValidationError("User with this email already exists")

        # Create new user
        user = await self.user_repo.create_user(
            name=user_data.name.strip(),
            email=clean_email,
            password=user_data.password,
            role_name=user_data.role_name,
            department=user_data.department,
        )

        # Create tokens
        role_name = user.role.name.lower() if user.role else "viewer"
        access_token = create_access_token(user_id=user.id, role=role_name)
        refresh_token = create_refresh_token(user_id=user.id)

        # Store refresh token
        refresh_expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=7)
        await self.user_repo.add_refresh_token(user, refresh_token, refresh_expires)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserOut.model_validate(user),
        )

    async def authenticate_user(self, login_data: LoginRequest) -> TokenPair:
        # Find user by email or username
        email = login_data.email
        if not email and login_data.username:
            # Assuming username is email for now, or add logic to find by username
            email = login_data.username
            
        if not email:
            raise UnauthorizedError("Email or username is required")

        clean_email = email.strip().lower()
        user = await self.user_repo.get_by_email(clean_email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        # Create tokens
        role_name = user.role.name.lower() if user.role else "viewer"
        access_token = create_access_token(user_id=user.id, role=role_name)
        refresh_token = create_refresh_token(user_id=user.id)

        # Store refresh token
        refresh_expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=7)
        await self.user_repo.add_refresh_token(user, refresh_token, refresh_expires)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserOut.model_validate(user),
        )

    async def refresh_token(self, refresh_data: RefreshRequest) -> TokenPair:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user_id = int(payload.get("sub")) if payload.get("sub") else None
        if not user_id:
            raise UnauthorizedError("Invalid refresh token")

        # Get user by refresh token
        user = await self.user_repo.get_by_refresh_token(refresh_data.refresh_token)
        if not user:
            raise UnauthorizedError("Invalid refresh token")

        # Create new tokens
        role_name = user.role.name.lower() if user.role else "viewer"
        access_token = create_access_token(user_id=user.id, role=role_name)
        new_refresh_token = create_refresh_token(user_id=user.id)

        # Revoke old refresh token
        await self.user_repo.revoke_refresh_token(refresh_data.refresh_token)

        # Store new refresh token
        refresh_expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=7)
        await self.user_repo.add_refresh_token(user, new_refresh_token, refresh_expires)

        return TokenPair(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserOut.model_validate(user),
        )

    async def logout_user(self, refresh_token: str) -> None:
        await self.user_repo.revoke_refresh_token(refresh_token)

    async def get_current_user(self, user_id: int) -> Optional[UserOut]:
        user = await self.user_repo.get(user_id)
        if user:
            return UserOut.model_validate(user)
        return None
