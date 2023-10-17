import re

from pydantic import BaseModel, EmailStr, field_validator


class UserSchemaCreated(BaseModel):
    username: str


class UserSchemaAdd(UserSchemaCreated):
    email: EmailStr
    # https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a
    # Minimum eight characters, at least one uppercase letter,
    # one lowercase letter and one number
    # Got error after using look-ahead (?=), not supported
    # password: str = Field(
    #     pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]$'
    # )
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r'[a-z]', password):
            raise ValueError(
                'Password should have at least one lowercase letter'
            )
        if not re.search(r'[A-Z]', password):
            raise ValueError(
                'Password should have at least one uppercase letter'
            )
        if not re.search(r'\d', password):
            raise ValueError('Password should have at least one digit')
        if not re.match(r'^[a-zA-Z\d]*$', password):
            raise ValueError('Password should contain only letters and digits')
        if len(password) < 8:
            raise ValueError('Password should be at least 8 characters long')
        return password


class UserAuthSchema(BaseModel):
    username: str
    password: str


class UserWithHashedPasswordAdd(UserSchemaCreated):
    email: EmailStr
    hashed_password: str
