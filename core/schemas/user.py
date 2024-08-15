from pydantic import BaseModel
from typing import List, Optional
from .common import BookBase
from .common import UserBase


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    books: List[BookBase] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
