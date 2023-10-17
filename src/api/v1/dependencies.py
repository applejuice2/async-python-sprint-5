from fastapi import HTTPException
from fastapi import Depends, Form
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from jose import JWTError
from jose.exceptions import ExpiredSignatureError

from db.db import async_session
from core.config import token_settings
from models.entities import User
from services.user import UserService
from services.file import FileService
from repositories.user import user_repository
from repositories.file import file_repository
from schemas.file import UploadFileSchema


def get_session() -> AsyncSession:
    return async_session()


def user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session, user_repository)


def file_service(session: AsyncSession = Depends(get_session)) -> FileService:
    return FileService(session, file_repository)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='v1/auth/sign_in')


async def get_user_from_token(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    CREDENTIAL_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )
    TOKEN_EXPIRED_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Token has expired',
    )
    try:
        payload = jwt.decode(
            token=token,
            key=token_settings.secret_key,
            algorithms=[token_settings.algorithm],
        )
        user_id: str = payload.get('sub')
        if user_id is None:
            raise CREDENTIAL_EXCEPTION
    except ExpiredSignatureError:
        raise TOKEN_EXPIRED_EXCEPTION
    except JWTError:
        raise CREDENTIAL_EXCEPTION
    user = await user_repository.get_one(session=session, id=user_id)
    if user is None:
        raise CREDENTIAL_EXCEPTION
    return user


def get_upload_schema(path_data: str = Form(...)) -> UploadFileSchema:
    try:
        return UploadFileSchema.parse_raw(path_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid path data") from e
