import logging

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import user_service
from schemas.user import UserSchemaCreated
from schemas.user import UserSchemaAdd
from schemas.auth_token import TokenSchema
from services.user import UserService

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)

logger = logging.getLogger(__name__)


@router.post(
    '/sign_up',
    response_model=UserSchemaCreated,
    status_code=status.HTTP_201_CREATED,
    description='Create a new User',
    response_description='Created Username',
)
async def add_user(
    user: UserSchemaAdd,
    user_service: UserService = Depends(user_service),
):
    username = await user_service.add_user(user)
    if not username:
        logger.warning(
            f'Error when creating new user with username {username}.'
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Username {user.username} is already used.'
        )
    logger.info(f'New user {username} was created.')
    return {'username': username}


@router.post(
    '/sign_in',
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
    description='Generate JWT Token',
    response_description='Generated JWT Token',
)
async def get_user_token(
    user: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(user_service),
):
    token, token_type = await user_service.get_user_token(user)
    if not token:
        logger.warning(
            f'Error when generating new JWT for {user.username}.'
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error when generating JWT'
        )
    logger.info(f'Token for {user.username} was created.')
    return {'access_token': token, 'token_type': token_type}
