from models.entities import User as UserModel
from schemas.user import UserSchemaAdd
from utils.repository import SQLAlchemyRepository


class RepositoryUser(
    SQLAlchemyRepository[
        UserModel, UserSchemaAdd
    ]
):
    pass


user_repository = RepositoryUser(UserModel)
