import string
from typing import Final
from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

from .database import db


class DatabaseColumnBase(DeclarativeBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


ALLOW_CHAR_IN_NAMES: Final[str] = string.ascii_letters + string.digits + "-_"
DISABLE_WORDS_IN_NAMES: Final[set[str]] = {
    "api",
    "static",
    "admin",
    "login",
    "logout",
    "register",
    "about",
}


def verify_name(name: str) -> bool:
    if name in DISABLE_WORDS_IN_NAMES:
        return False
    if len(name) <= 1:
        return False
    if not all([c in ALLOW_CHAR_IN_NAMES for c in name]):
        return False
    if len(name) > 50:
        return False
    return True


def get_password_hash(password: str, name: str = "") -> str:
    return name + "|" + password


def verify_password_hash(password_hash: str, password: str, name: str = "") -> bool:
    return password_hash == get_password_hash(password, name=name)


class Note(DatabaseColumnBase):
    __tablename__ = "note"

    name = Column(String, unique=True)
    content = Column(String)
    clip_version = Column(Integer)
    password = Column(String, nullable=True)
    viewonly_url = Column(String, unique=True)
    timeout_days = Column(Integer)
