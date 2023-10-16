from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from schemas.user import UserSchemaAdd, UserWithHashedPasswordAdd
from utils.repository import AbstractRepository
from models.entities import User as UserModel
from utils.token import Hasher, create_access_token
from core.config import token_settings


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: AbstractRepository
    ):
        self.session: AsyncSession = session
        self.user_repo: AbstractRepository = user_repo

    async def add_user(self, user: UserSchemaAdd):
        hashed_password = Hasher.get_password_hash(user.password)
        user_with_hashed_password = UserWithHashedPasswordAdd(
            username=user.username,
            hashed_password=hashed_password,
            email=user.email
        )
        try:
            user_model: UserModel = await self.user_repo.add_one(
                self.session,
                user_with_hashed_password
            )
        except IntegrityError:
            return
        username = user_model.username
        return username
    
    async def get_user_token(self, user: OAuth2PasswordRequestForm):
        token_type = 'bearer'
        user_instanse: UserModel = await self.user_repo.get_one(
            self.session,
            username=user.username
        )
        if not user_instanse:
            return None, token_type
        if not Hasher.verify_password(user.password, user_instanse.hashed_password):
            return None, token_type

        access_token_expires = timedelta(
            minutes=token_settings.access_token_expire_minutes
        )
        access_token = create_access_token(
            data={'sub': user_instanse.email, 'other_custom_data': [1, 2, 3, 4]},
            expires_delta=access_token_expires,
        )
        return access_token, token_type
