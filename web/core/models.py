from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, DateTime, Integer, String

from web.core.db import Base


class Book(Base):
    """Модель таблицы книг."""
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(254), nullable=False)
    author = Column(String(254), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.now)

    def __str__(self):
        return self.name[:30]

    def dict(self):
        return dict(name=self.name,
                    id=self.id,
                    author=self.author,
                    uploaded_at=self.uploaded_at)


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    Наследуется от модели пользователя из библиотеки FastAPI Users.
    """

    def to_dict(self):
        return dict(
            id=self.id,
            email=self.email,
            is_superuser=self.is_superuser,
        )
