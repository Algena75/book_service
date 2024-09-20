from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field, field_validator


class BookUpdate(BaseModel):
    name: Union[str, None] = Field(min_length=1)
    author: Union[str, None] = Field(min_length=1)

    @field_validator('name', 'author')
    @classmethod
    def check_string(cls, value: str) -> str:
        if value:
            if len(value.strip()) == 0:
                raise ValueError('Поле не может быть пустым')
            return value.strip()


class BookCreate(BookUpdate):
    name: str
    author: str


class BookRead(BookCreate):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
