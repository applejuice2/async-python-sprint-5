import uuid

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(length=30), nullable=False, unique=True)
    email = Column(EmailType, nullable=False)
    hashed_password = Column(String, nullable=False)

    __mapper_args__ = {'eager_defaults': True}

    def __repr__(self):
        return 'User(username="%s")' % (self.username)