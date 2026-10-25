from __future__ import annotations

import datetime as dt
from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import RefreshToken, Role, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get(self, id_: int) -> Optional[User]:
        stmt = select(User).options(selectinload(User.role)).where(User.id == id_)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt: Select = select(User).options(selectinload(User.role)).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_refresh_token(self, token: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.role))
            .join(RefreshToken, RefreshToken.user_id == User.id)
            .where(RefreshToken.token == token)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, *, name: str, email: str, password: str, role_name: str, department: Optional[str] = None) -> User:
        # Get or create role
        role = await self.session.execute(select(Role).where(Role.name == role_name))
        role = role.scalar_one_or_none()
        if role is None:
            role = Role(name=role_name, description=f"{role_name} role")
            self.session.add(role)
            await self.session.flush()
        
        user = User(
            name=name,
            email=email.lower(),
            hashed_password=hash_password(password),
            department=department,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_users(self, *, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(User).options(selectinload(User.role)).order_by(User.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_refresh_token(self, user: User, token: str, expires_at: dt.datetime) -> RefreshToken:
        rt = RefreshToken(token=token, user_id=user.id, expires_at=expires_at)
        self.session.add(rt)
        await self.session.flush()
        return rt

    async def revoke_refresh_token(self, token: str) -> None:
        rt = await self.session.execute(select(RefreshToken).where(RefreshToken.token == token))
        rt = rt.scalar_one_or_none()
        if rt:
            await self.session.delete(rt)
            await self.session.flush()
