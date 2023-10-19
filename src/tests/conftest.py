import asyncio
from typing import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy import delete

from main import app
from core.config import app_settings
from models.entities import User, File


engine_test = create_async_engine(
    str(app_settings.database_dsn),
    echo=app_settings.echo,
    future=True
)
SessionLocal = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)

# Таблицы
TABLES = [User, File]
# Путь до директории, где сохраняются тестовые файлы
TEST_FILES_DIRECTORY = app_settings.mountpoint


# @pytest_asyncio.fixture(scope="function")
# async def clean_database():
#     # Очистка до теста
#     async with SessionLocal() as session:
#         for table in TABLES:
#             await session.execute(delete(table))
#         await session.commit()

#     # Запуск теста
#     yield

#     # Очистка после теста
#     async with SessionLocal() as session:
#         for table in TABLES:
#             await session.execute(delete(table))
#         await session.commit()
@pytest_asyncio.fixture(scope="function")
async def clean_before_database():
    # Очистка до теста
    async with SessionLocal() as session:
        for table in TABLES:
            await session.execute(delete(table))
        await session.commit()

    # Запуск теста
    yield


@pytest_asyncio.fixture(scope="function")
async def clean_after_database():
    # Запуск теста
    yield

    # Очистка после теста
    async with SessionLocal() as session:
        for table in TABLES:
            await session.execute(delete(table))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def clean_before_filesystem():
    # NOTE Удаляем все файлы внутри каталога
    # перед выполнением теста (на всякий случай)
    for root, dirs, files in os.walk(TEST_FILES_DIRECTORY, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    # Запуск теста
    yield


@pytest_asyncio.fixture(scope="function")
async def clean_after_filesystem():
    # Запуск теста
    yield

    # NOTE Удаляем все файлы внутри каталога после выполнения теста
    for root, dirs, files in os.walk(TEST_FILES_DIRECTORY, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


# SETUP
@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(ac: AsyncClient) -> dict:
    """Фикстура для регистрации пользователя."""
    user_data = {
        "username": "appleJUICE2",
        "email": "apple@juice.com",
        "password": "testPASSWORD99"
    }

    await ac.post('/api/v1/auth/sign_up', json=user_data)

    return user_data


@pytest_asyncio.fixture(scope="function")
async def token(ac: AsyncClient, test_user) -> str:
    """Фикстура для создания пользователя и JWT токена"""
    data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }

    response = await ac.post("/api/v1/auth/sign_in", data=data)

    jwt_token = response.json().get("access_token")
    return jwt_token
