from uuid import UUID
from datetime import datetime
from typing import Optional
import re

from pydantic import field_validator, root_validator
from pydantic import BaseModel

from core.config import app_settings


class UploadFileSchema(BaseModel):
    path: str

    @staticmethod
    def add_starting_slash(path: str) -> str:
        """
        Добавляет слэш в начало каждого переданного пользователями пути.
        """
        return path if path.startswith('/') else '/' + path

    @staticmethod
    def is_path_safe(path: str) -> bool:
        """
        Проверяет, безопасен ли путь для использования.
        Относительные пути вроде '../' считаются небезопасными.
        """
        return not re.search(r'(\.\./)|(\.\.\$)', path)

    @field_validator('path')
    @classmethod
    def add_prefix_to_path(cls, path):
        """
        Добавляем в каждый путь необходимый префикс,
        чтобы файлы и директории создавались в строго отведенной Volume.
        """
        if not cls.is_path_safe(path):
            raise ValueError('Your path should not contain dots')

        path = cls.add_starting_slash(path)
        prefix_path = app_settings.mountpoint
        return prefix_path + path


class CreateFileSchema(BaseModel):
    path: str
    name: str
    size: int
    is_downloadable: bool = True
    user_id: UUID


class UploadedFileSchema(BaseModel):
    id: UUID
    path: str
    name: str
    created_at: datetime
    size: int
    is_downloadable: bool = True

    class Config:
        from_attributes = True


class UploadedFileWithoutVolumePathSchema(UploadedFileSchema):
    @field_validator('path')
    @classmethod
    def delete_prefix_from_path(cls, path):
        """
        Удаляем из пути необходимый префикс,
        чтобы не показывать его пользователю и чтобы он видел именно тот путь,
        который он указал в запросе.
        """
        prefix_path = app_settings.mountpoint
        if path.startswith(prefix_path):
            return path[len(prefix_path):]
        return path


class ListofUploadFilesSchema(BaseModel):
    account_id: UUID
    files: list[UploadedFileWithoutVolumePathSchema]


class FileDownloadSchema(BaseModel):
    path: Optional[str]
    id: Optional[UUID]

    @root_validator(pre=True)
    def check_required_fields(cls, values):
        if not values.get('path') and not values.get('id'):
            raise ValueError('You must provide either a path or an ID.')
        return values

    @staticmethod
    def add_starting_slash(path: str) -> str:
        """
        Гарантирует наличие слеша в начале пути.
        """
        if path:
            return path if path.startswith('/') else '/' + path
        return path

    @field_validator('path')
    @classmethod
    def add_prefix_to_path(cls, path):
        """
        Добавляем в каждый путь необходимый префикс,
        чтобы файлы скачивались из директорий в Volume, где они
        изначально сохранялись.
        """
        if path:
            path = cls.add_starting_slash(path)
            prefix_path = app_settings.mountpoint
            path = prefix_path + path
        return path
