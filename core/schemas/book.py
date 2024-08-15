from typing import Optional
from .common import BookBase
from .common import UserBase

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    author: Optional[UserBase] = None

    class Config:
        orm_mode = True

class BookUpdate(BookBase):
    title: Optional[str]

    class Config:
        orm_mode = True
