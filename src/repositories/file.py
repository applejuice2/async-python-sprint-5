from models.entities import File as FileModel
from schemas.file import UploadFileSchema
from utils.repository import SQLAlchemyRepository


class RepositoryFile(
    SQLAlchemyRepository[
        FileModel, UploadFileSchema
    ]
):
    pass


file_repository = RepositoryFile(FileModel)
