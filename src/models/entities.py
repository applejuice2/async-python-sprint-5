import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.exc import ArgumentError

from .base import Base


class PositiveInteger(TypeDecorator):
    impl = Integer

    def process_bind_param(self, value, dialect):
        if value is not None and value < 0:
            raise ArgumentError('Value should be a positive integer.')
        return value


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(length=30), nullable=False, unique=True)
    email = Column(EmailType, nullable=False)
    hashed_password = Column(String, nullable=False)

    files = relationship('File', back_populates='user', passive_deletes=True)

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self):
        return 'User(username="%s")' % (self.username)


class File(Base):
    __tablename__ = "file"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String(length=255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # NOTE Путь и так будет уникальным, так как на 
    # уровне сервиса уже есть проверка в ФС, чтобы выкидывалось 
    # исключение, если по указанному пути уже есть файл/директория.
    path = Column(String(length=255), nullable=False)
    size = Column(PositiveInteger)
    is_downloadable = Column(Boolean, default=True)

    user = relationship('User', back_populates='files')

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self):
        return 'File(name="%s")' % (self.name)
