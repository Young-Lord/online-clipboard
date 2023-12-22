from abc import ABC
import string
from typing import Optional, Final
import uuid

from flask_sqlalchemy import SQLAlchemy

from .base import Note

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


class Datastore(ABC):
    def __init__(self, _db: SQLAlchemy):
        self.session = _db.session


class NoteDatastore(Datastore):
    def __init__(self, _db):
        super().__init__(_db)

    def get_note(self, name: str) -> Optional[Note]:
        if not verify_name(name):
            return None
        return self.session.query(Note).filter_by(name=name).first()

    def update_note(
        self,
        name: str,
        clip_version: int,
        content: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        note: Optional[Note] = self.session.query(Note).filter_by(name=name).first()
        if note is None:
            note = Note(
                name=name,
            )
        if content is not None:
            note.content = content
        if password is not None:
            note.password = get_password_hash(password, name)
        note.clip_version = clip_version
        note.viewonly_url = uuid.uuid4().hex
        note.timeout_days = 30
        self.session.add(note)
        self.session.commit()

    def delete_note(
        self,
        name: str,
    ) -> None:
        note: Optional[Note] = self.session.query(Note).filter_by(name=name).first()
        if note is not None:
            self.session.delete(note)
            self.session.commit()
