from abc import ABC
import os
import string
from typing import Optional, Final
import uuid
from sqlalchemy import Column, DateTime, func, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from app.config import Config

from app.note_const import (
    ALLOW_CHAR_IN_NAMES,
    DISABLE_WORDS_IN_NAMES,
    READONLY_PREFIX,
    Metadata,
)
from .base import DatabaseColumnBase, db
from flask_sqlalchemy import SQLAlchemy


class Note(db.Model, DatabaseColumnBase):
    __tablename__ = "notes"

    name: Mapped[str] = mapped_column(String, unique=True)
    content: Mapped[str] = mapped_column(String)
    clip_version: Mapped[int] = mapped_column(Integer)
    password: Mapped[str] = mapped_column(String, nullable=True)
    readonly_name: Mapped[str] = mapped_column(String, unique=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer)
    files: Mapped[set["File"]] = relationship("File", back_populates="note")

    def __repr__(self):
        return f"<Note {self.name}>"


class File(db.Model, DatabaseColumnBase):
    __tablename__ = "files"

    filename: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"))
    note: Mapped["Note"] = relationship("Note", back_populates="files")
    file_size: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"<File {self.filename}> in {self.note.name} ({self.note.id})>"


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


def verify_timeout_seconds(timeout_seconds: int) -> bool:
    return 1 <= timeout_seconds <= Metadata.max_timeout


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

    def get_note_by_readonly_name(self, readonly_name: str) -> Optional[Note]:
        return self.session.query(Note).filter_by(readonly_name=readonly_name).first()

    def update_note(
        self,
        name: str,
        clip_version: int = 1,
        content: Optional[str] = None,
        password: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        note: Optional[Note] = self.session.query(Note).filter_by(name=name).first()
        if note is None:
            note = Note(
                name=name,
            )
            note.content = ""
            note.clip_version = clip_version
            note.readonly_name = READONLY_PREFIX + uuid.uuid4().hex
            note.timeout_seconds = Metadata.default_timeout
        if content is not None:
            note.content = content
        if password is not None:
            note.password = get_password_hash(password, name)
        if timeout_seconds is not None:
            if not verify_timeout_seconds(timeout_seconds):
                raise ValueError("Invalid timeout_seconds")
            note.timeout_seconds = timeout_seconds
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

    def add_file(
        self, note: Note, filename: str, file_path: str, file_size: int
    ) -> None:
        file = File(
            filename=filename, file_path=file_path, note=note, file_size=file_size
        )
        self.session.add(file)
        self.session.commit()

    def delete_file(self, file: File) -> None:
        file_path = file.file_path
        try:
            os.remove(file_path)
        except:
            pass
        self.session.delete(file)
        self.session.commit()

    def get_file(self, file_id) -> Optional[File]:
        file: Optional[File] = self.session.query(File).filter_by(id=file_id).first()
        return file
