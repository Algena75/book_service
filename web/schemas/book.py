from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class BookUpdate(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None

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
    uploaded_at: datetime | str

    class Config:
        from_attributes = True

    @field_validator("uploaded_at")
    def parse_date(cls, value):
        if isinstance(value, str):
            return value
        return value.date().strftime("%d-%m-%Y")
