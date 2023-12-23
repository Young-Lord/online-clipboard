from datetime import datetime
from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


class DatabaseColumnBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
