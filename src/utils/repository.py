from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from models.base import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, *args, **kwargs):
        raise NotImplementedError

    async def get_one(self, *args, **kwargs):
        raise NotImplementedError

    async def edit_one(self, *args, **kwargs):
        raise NotImplementedError

    async def add_many(self, *args, **kwargs):
        raise NotImplementedError

    async def get_many(self, *args, **kwargs):
        raise NotImplementedError

    async def get_one_with_dependencies(self, *args, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(
    AbstractRepository,
    Generic[ModelType,
            CreateSchemaType]
):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def add_one(
        self, session: AsyncSession, obj: CreateSchemaType
    ) -> ModelType:
        obj_dict = obj.model_dump()
        stmt = insert(self.model).values(**obj_dict).returning(self.model)
        res = await session.execute(stmt)
        result_object = res.fetchone()
        await session.commit()
        return result_object

    async def get_one(
        self, session: AsyncSession, **filter_by: Any
    ) -> ModelType:
        stmt = select(self.model).filter_by(**filter_by)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def add_many(
        self,
        session: AsyncSession,
        objs: list[CreateSchemaType],
    ) -> list[ModelType]:
        data = [obj.model_dump() for obj in objs]
        stmt = insert(self.model).values(data).returning(self.model)
        res = await session.execute(stmt)
        result_objects = res.fetchall()
        await session.commit()
        return result_objects

    async def get_many(
        self,
        session: AsyncSession,
        **filter_by: Any,
    ) -> list[ModelType]:
        stmt = select(self.model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_one_with_dependencies(
        self,
        session: AsyncSession,
        dependencies: list[str] = [],
        **filter_by: Any,
    ) -> ModelType:
        stmt = select(self.model).filter_by(**filter_by)
        for dependency in dependencies:
            attr = getattr(self.model, dependency, None)
            if attr:
                stmt = stmt.options(joinedload(attr))

        result = await session.execute(stmt)
        return result.scalars().unique().one_or_none()
