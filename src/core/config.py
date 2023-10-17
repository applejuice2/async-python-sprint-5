import os
from logging import config as logging_config

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    app_title: str = 'FileUploaderApp'
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_host: str = '127.0.0.1'
    project_port: int = 8000
    echo: bool = True
    database_dsn: PostgresDsn
    mountpoint: str

    class Config:
        extra = 'ignore'


class TokenSettings(BaseSettings):
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30

    class Config:
        extra = 'ignore'


app_settings = AppSettings()
token_settings = TokenSettings()
