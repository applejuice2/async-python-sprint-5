from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from db.db import async_session
from services.user import UserService
from repositories.user import user_repository


def get_session() -> AsyncSession:
    return async_session()


def user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session, user_repository)