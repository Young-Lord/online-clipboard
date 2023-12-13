from abc import ABC
import string
from typing import Optional

from flask_sqlalchemy import SQLAlchemy

from .base import Note


class Datastore(ABC):
    def __init__(self, _db: SQLAlchemy):
        self.session = _db.session


class NoteDatastore(Datastore):
    def __init__(self, _db):
        super().__init__(_db)

    def get_content(self, name: str) -> Optional[Note]:
        return self.session.query(Note).filter_by(name=name).first()

    def update_note(
        self, name: str, content: Optional[str], password: str = ""
    ) -> None:
        note = self.session.query(Note).filter_by(name=name).first()
        if note is None:
            note = Note(
                name=name,
            )
            self.session.add(note)
        else:
            note.content = content
            note.password = password
        self.session.commit()
