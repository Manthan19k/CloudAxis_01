from __future__ import annotations

from typing import List, Optional

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserOut


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: int) -> Optional[UserOut]:
        user = await self.user_repo.get(user_id)
        if user:
            return UserOut.model_validate(user)
        return None

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserOut]:
        user = await self.user_repo.get(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.user_repo.update(user)
        return UserOut.model_validate(user)

    async def list_users(self, *, skip: int = 0, limit: int = 100) -> List[UserOut]:
        users = await self.user_repo.list_users(skip=skip, limit=limit)
        return [UserOut.model_validate(user) for user in users]

    async def delete_user(self, user_id: int) -> bool:
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        await self.user_repo.delete(user)
        return True
