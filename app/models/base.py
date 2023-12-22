from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

from .database import db


class DatabaseColumnBase(DeclarativeBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Note(db.Model, DatabaseColumnBase):
    __tablename__ = "note"

    name: Mapped[str] = mapped_column(String, unique=True)
    content: Mapped[str] = mapped_column(String)
    clip_version: Mapped[int] = mapped_column(Integer)
    password: Mapped[str] = mapped_column(String, nullable=True)
    viewonly_url: Mapped[str] = mapped_column(String, unique=True)
    timeout_days: Mapped[int] = mapped_column(Integer)
