from sqlalchemy import Column, DateTime, func, Integer, String

from .database import db


class Base(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Note(Base):
    name = Column(String)
    content = Column(String)
    password = Column(String)
    viewonly_url = Column(String)
    timeout_days = Column(Integer)