from pydantic import BaseModel
from typing import Literal


class BookBase(BaseModel):
    title: str
    status: Literal["read", "to_read"]


class UserBase(BaseModel):
    username: str
    email: str
