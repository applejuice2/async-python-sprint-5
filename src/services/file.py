from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import File
from fastapi.exceptions import HTTPException

from schemas.file import (
    CreateFileSchema,
    FileDownloadSchema,
    UploadFileSchema,
    UploadedFileSchema,
    UploadedFileWithoutVolumePathSchema
)
from utils.repository import AbstractRepository
from models.entities import File as FileModel
from models.entities import User as UserModel


class FileService:
    def __init__(
        self,
        session: AsyncSession,
        file_repo: AbstractRepository
    ):
        self.session: AsyncSession = session
        self.file_repo: AbstractRepository = file_repo

    async def add_file(
        self, user: UserModel, file: File, path_data: UploadFileSchema
    ) -> dict:

        path_str = str(path_data.path)

        # NOTE Если путь заканчивается на слэш, то это директория
        if path_str.endswith('/'):
            final_path = Path(path_str) / file.filename
        else:
            # NOTE Иначе это имя файла
            final_path = Path(path_str)

        # Проверка, существует ли уже файл по указанному пути в ФС.
        if final_path.exists():
            raise HTTPException(
                status_code=400,
                detail=(
                    f'Path {final_path} is busy. '
                    'Please choose a different name.'
                )
            )

        # NOTE Создаем необходимые директории
        try:
            final_path.parent.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise HTTPException(
                status_code=400, 
                detail=(
                    'Cannot create directory because a file '
                    f'named {final_path.parent.name} already exists.'
                )
            )

        # NOTE Сохраняем файл и находим его размер
        with final_path.open('wb') as buffer:
            buffer.write(await file.read())
        file_size = final_path.stat().st_size

        file_model: FileModel = await self.file_repo.add_one(
            self.session,
            CreateFileSchema(
                user_id=user.id,
                path=str(final_path),
                name=final_path.name,
                size=file_size,
            )
        )

        return (
            UploadedFileWithoutVolumePathSchema
            .from_orm(file_model)
            .model_dump()
        )

    async def get_user_files(self, user: UserModel) -> list[dict]:
        file_models: list[FileModel] = (
            await self.file_repo.get_many(self.session, user_id=user.id)
        )

        return [
            UploadedFileSchema.from_orm(file).model_dump()
            for file in file_models
        ]

    async def get_file_path(
        self,
        file_data: FileDownloadSchema,
        user: UserModel
    ) -> Optional[str]:
        if file_data.id:
            file_model: FileModel = (
                await self.file_repo.get_one(self.session, id=file_data.id)
            )
        else:
            file_model: FileModel = (
                await self.file_repo.get_one(self.session, path=file_data.path)
            )

        if not file_model:
            return

        # NOTE Если файл не принадлежит пользователю,
        # то не даём возможность скачивать файл.
        if user.id != file_model.user_id:
            return

        return file_model.path
