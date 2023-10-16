from core.config import app_settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    str(app_settings.database_dsn),
    echo=app_settings.echo,
    future=True
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
