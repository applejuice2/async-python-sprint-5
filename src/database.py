from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

from core.config import app_settings
from models.entities import User
from models.base import Base


async def main():
    engine = create_async_engine(
        str(app_settings.database_dsn),
        echo=True,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


asyncio.run(main())
