from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped

if TYPE_CHECKING:
    from sqlalchemy.orm import mapped_column
else:
    try:
        from sqlalchemy.orm import mapped_column
    except:
        # SQLAlchemy 1: https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#step-two-replace-declarative-use-of-schema-column-with-orm-mapped-column
        from sqlalchemy import Column as mapped_column
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


class DatabaseColumnBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, unique=True, autoincrement=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
