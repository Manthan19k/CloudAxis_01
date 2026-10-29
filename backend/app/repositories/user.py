from __future__ import annotations

import datetime as dt
from typing import List, Optional

from sqlalchemy import Select, func, select
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
        clean_email = email.strip().lower() if email else ""
        stmt: Select = select(User).options(selectinload(User.role)).where(func.lower(User.email) == clean_email)
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
        norm_role = role_name.lower().strip() if role_name else "engineer"
        role_stmt = select(Role).where(func.lower(Role.name) == norm_role)
        role = (await self.session.execute(role_stmt)).scalar_one_or_none()
        if role is None:
            role = Role(name=norm_role, description=f"{norm_role.capitalize()} role")
            self.session.add(role)
            await self.session.flush()
        
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            hashed_password=hash_password(password),
            department=department,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        created_user = await self.get(user.id)
        return created_user or user

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
