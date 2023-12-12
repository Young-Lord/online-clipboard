from abc import ABC

from flask_sqlalchemy import SQLAlchemy

from .base import Note


class Datastore(ABC):

    def __init__(self, _db: SQLAlchemy):
        self.session = _db.session


class NoteDatastore(Datastore):

    def __init__(self, _db):
        super().__init__(_db)

    def get_content(self, name: str):
        return self.session.query(Note).filter_by(name=name).first()
