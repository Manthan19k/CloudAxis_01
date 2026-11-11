from __future__ import annotations

from typing import List, Optional

from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, ValidationError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserOut


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: int) -> Optional[UserOut]:
        user = await self.user_repo.get(user_id)
        if user:
            return UserOut.model_validate(user)
        return None

    async def create_user(self, user_data: UserCreate) -> UserOut:
        clean_email = user_data.email.strip().lower()
        existing = await self.user_repo.get_by_email(clean_email)
        if existing:
            raise ConflictError("User with this email already exists")

        target_role = user_data.role_name.strip().lower() if user_data.role_name else "engineer"
        role = await self.user_repo.get_role_by_name(target_role)
        if not role:
            raise BadRequestError(f"Role '{user_data.role_name}' does not exist")

        user = await self.user_repo.create_user(
            name=user_data.name.strip(),
            email=clean_email,
            password=user_data.password,
            role_name=target_role,
            department=user_data.department,
        )
        return UserOut.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
        current_user_id: Optional[int] = None,
    ) -> Optional[UserOut]:
        user = await self.user_repo.get(user_id)
        if not user:
            return None

        # 1. Role update support & Admin protection
        if user_data.role_name is not None:
            target_role = user_data.role_name.strip().lower()
            role = await self.user_repo.get_role_by_name(target_role)
            if not role:
                raise BadRequestError(f"Role '{user_data.role_name}' does not exist")

            current_is_admin = bool(user.role and user.role.name.lower() == "admin")
            new_is_admin = bool(role.name.lower() == "admin")
            if current_is_admin and not new_is_admin and user.is_active:
                active_admins = await self.user_repo.count_active_admins()
                if active_admins <= 1:
                    raise ConflictError("Cannot remove admin role from the last active administrator")

            user.role = role
            user.role_id = role.id

        # 2. Deactivation & Self-deactivation protection
        if user_data.is_active is not None:
            if user_data.is_active is False and user.is_active is True:
                # Prevent self-deactivation
                if current_user_id is not None and current_user_id == user.id:
                    raise ForbiddenError("Administrators cannot deactivate their own account")

                # Prevent deactivation of the last active administrator
                if user.role and user.role.name.lower() == "admin":
                    active_admins = await self.user_repo.count_active_admins()
                    if active_admins <= 1:
                        raise ConflictError("Cannot deactivate the last active administrator")
            user.is_active = user_data.is_active

        # 3. Update profile fields
        if user_data.name is not None:
            user.name = user_data.name.strip()
        if user_data.email is not None:
            new_email = user_data.email.strip().lower()
            if new_email != user.email:
                existing = await self.user_repo.get_by_email(new_email)
                if existing and existing.id != user.id:
                    raise ValidationError("User with this email already exists")
                user.email = new_email
        if user_data.department is not None:
            user.department = user_data.department

        await self.user_repo.update(user)
        refreshed = await self.user_repo.get(user.id)
        return UserOut.model_validate(refreshed or user)

    async def list_users(self, *, skip: int = 0, limit: int = 100) -> List[UserOut]:
        users = await self.user_repo.list_users(skip=skip, limit=limit)
        return [UserOut.model_validate(user) for user in users]

    async def delete_user(
        self,
        user_id: int,
        current_user_id: Optional[int] = None,
    ) -> bool:
        user = await self.user_repo.get(user_id)
        if not user:
            return False

        # Prevent self-deletion
        if current_user_id is not None and current_user_id == user.id:
            raise ForbiddenError("Administrators cannot delete their own account")

        # Prevent deletion of the last active administrator
        if user.role and user.role.name.lower() == "admin" and user.is_active:
            active_admins = await self.user_repo.count_active_admins()
            if active_admins <= 1:
                raise ConflictError("Cannot delete the last active administrator")

        await self.user_repo.delete(user)
        return True
