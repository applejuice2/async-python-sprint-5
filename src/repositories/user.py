from typing import Any

from models.entities import User as UserModel
from schemas.user import UserSchemaAdd
from utils.repository import SQLAlchemyRepository


class RepositoryURL(
    SQLAlchemyRepository[
        UserModel, UserSchemaAdd, Any
    ]
):
    pass


user_repository = RepositoryURL(UserModel)
