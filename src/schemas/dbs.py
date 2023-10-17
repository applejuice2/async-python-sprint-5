from pydantic import BaseModel


class DBStatusSchema(BaseModel):
    detail: str
