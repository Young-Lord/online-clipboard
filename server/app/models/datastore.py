from abc import ABC
import datetime
import os
from typing import Optional
import uuid
from sqlalchemy import Boolean, Integer, String, ForeignKey, func, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.note_const import PASSWORD_SCHEMES
from passlib.context import CryptContext
from app.note_const import (
    ALLOW_CHAR_IN_NAMES,
    DISABLE_WORDS_IN_NAMES,
    READONLY_PREFIX,
    Metadata,
)
from app.utils import sha512
from .base import DatabaseColumnBase, db
from flask_sqlalchemy import SQLAlchemy

passlib_context = CryptContext(schemes=PASSWORD_SCHEMES)


class Note(db.Model, DatabaseColumnBase):
    __tablename__ = "notes"

    name: Mapped[str] = mapped_column(String, unique=True)
    content: Mapped[str] = mapped_column(String)
    clip_version: Mapped[int] = mapped_column(Integer)
    password: Mapped[str] = mapped_column(
        String, nullable=False, default="", server_default=""
    )  # empty string for no password, passlib hash otherwise
    readonly_name: Mapped[str] = mapped_column(
        String, nullable=False
    )  # always non-empty
    has_readonly_name: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=sql.expression.true()
    )
    timeout_seconds: Mapped[int] = mapped_column(Integer)
    files: Mapped[list["File"]] = relationship("File", back_populates="note")
    all_file_size: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=sql.expression.literal(0),
    )
    user_property: Mapped[str] = mapped_column(
        String, default="{}", server_default="{}"
    )
    illegal_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default=sql.expression.literal(0)
    )
    ban_unitl: Mapped[datetime.datetime] = mapped_column(
        db.DateTime, nullable=True, default=None
    )

    @property
    def readonly_name_if_has(self) -> str:
        if self.has_readonly_name:
            return self.readonly_name
        return ""

    def __repr__(self):
        return f"<Note {self.name}>"

    @property
    def is_expired(self) -> bool:
        return (
            self.timeout_seconds is not None
            and self.timeout_seconds > 0
            and (
                datetime.datetime.now()
                > self.updated_at + datetime.timedelta(seconds=self.timeout_seconds)
            )
        )


class File(db.Model, DatabaseColumnBase):
    __tablename__ = "files"

    filename: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"))
    note: Mapped["Note"] = relationship("Note", back_populates="files")
    file_size: Mapped[int] = mapped_column(Integer)
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, default=Metadata.default_file_timeout
    )

    @property
    def is_expired(self) -> bool:
        return (
            self.timeout_seconds is not None
            and self.timeout_seconds > 0
            and (
                datetime.datetime.now()
                > self.updated_at + datetime.timedelta(seconds=self.timeout_seconds)
            )
        )

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


def combine_name_and_password(name: str, password: str) -> str:
    if password is None:
        password = ""
    return name + password


def combine_name_and_password_and_readonly(
    name: str, password: str, readonly_if_has: str
) -> str:
    return (
        combine_name_and_password(name, password)
        + readonly_if_has
        + ("1" if readonly_if_has else "0")
    )


def verify_timeout_seconds(timeout_seconds: int) -> bool:
    return 1 <= timeout_seconds <= Metadata.max_timeout


class Datastore(ABC):
    def __init__(self, _db: SQLAlchemy):
        self.session = _db.session

    def drop_it(self, *, yes_do_as_i_say: bool = False) -> None:
        assert yes_do_as_i_say
        self.session.query(Note).delete()
        self.session.query(File).delete()
        self.session.commit()


class NoteDatastore(Datastore):
    def get_note(self, name: str) -> Optional[Note]:
        if not verify_name(name):
            return None
        return self.session.query(Note).filter_by(name=name).first()

    def get_note_by_readonly_name(self, readonly_name: str) -> Optional[Note]:
        return (
            self.session.query(Note)
            .filter_by(readonly_name=readonly_name, has_readonly_name=True)
            .first()
        )

    def get_unique_readonly_name(self) -> str:
        while True:
            readonly_name = READONLY_PREFIX + uuid.uuid4().hex
            if self.get_note_by_readonly_name(readonly_name) is None:
                return readonly_name

    def update_note(
        self,
        name: str,
        clip_version: Optional[int] = None,
        content: Optional[str] = None,
        password: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        user_property: Optional[str] = None,
        enable_readonly: Optional[bool] = None,
    ) -> None:
        note: Optional[Note] = self.get_note(name)
        if note is None:
            note = Note(
                name=name,
            )
            note.content = ""
            if password is None:
                password = ""
            note.clip_version = 1
            enable_readonly = True
            note.timeout_seconds = Metadata.default_note_timeout
        if clip_version is not None:
            # only allow increasing or equal clip_version
            if clip_version < note.clip_version:
                raise ValueError("clip_version too low")
            note.clip_version = clip_version + 1
        if content is not None:
            note.content = content
        if password is not None:
            if password == "":
                note.password = ""
            else:
                note.password = passlib_context.hash(
                    combine_name_and_password(name, password)
                )
        if timeout_seconds is not None:
            if not verify_timeout_seconds(timeout_seconds):
                raise ValueError("Invalid timeout_seconds")
            note.timeout_seconds = timeout_seconds
        if user_property is not None:
            note.user_property = user_property
        if enable_readonly is not None:
            if enable_readonly:
                note.readonly_name = self.get_unique_readonly_name()
                note.has_readonly_name = True
            else:
                note.has_readonly_name = False
        self.session.add(note)
        self.session.commit()

    def delete_note(
        self,
        note: Note,
    ) -> None:
        """
        Delete a note and all its files.
        The object note will be invalid after this call.
        """
        for file in note.files:
            self.delete_file(file)
        self.session.delete(note)
        self.session.commit()

    def add_file(
        self, note: Note, filename: str, file_path: str, file_size: int
    ) -> None:
        file = File(
            filename=filename, file_path=file_path, note=note, file_size=file_size
        )
        self.session.add(file)
        note.all_file_size += file_size
        self.session.add(note)
        self.session.commit()

    def delete_file(self, file: File) -> None:
        file_path = file.file_path
        file.note.all_file_size -= file.file_size
        self.session.add(file.note)
        try:
            os.remove(file_path)
        except:
            pass
        self.session.delete(file)
        self.session.commit()

    def get_file(self, file_id) -> Optional[File]:
        file: Optional[File] = self.session.query(File).filter_by(id=file_id).first()
        return file

    def report_note(self, note: Note) -> None:  
        if note.illegal_count >= len(Metadata.illegal_ban_time):
            # max illegal count reached -> delete
            ban_time = -1
        else:
            ban_time = Metadata.illegal_ban_time[note.illegal_count]
        if ban_time == -1:
            self.delete_note(
                note,
            )
        else:
            note.illegal_count += 1
            note.ban_unitl = datetime.datetime.now() + datetime.timedelta(
                seconds=ban_time
            )
            self.session.add(note)
            self.session.commit()


datastore = NoteDatastore(db)
