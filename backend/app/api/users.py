from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.dependencies import get_user_repo


router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(user_repo = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


@router.get("/", response_model=List[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
):
    users = await user_service.list_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    if not user_id.isdigit():
        raise HTTPException(status_code=404, detail="User not found")
    user = await user_service.get_user(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(user_data)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    if not user_id.isdigit():
        raise HTTPException(status_code=404, detail="User not found")
    user = await user_service.update_user(int(user_id), user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    if not user_id.isdigit():
        raise HTTPException(status_code=404, detail="User not found")
    success = await user_service.delete_user(int(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
