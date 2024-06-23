from abc import ABC
import datetime
import os
import time
from typing import Any, Callable, NamedTuple, Optional
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey, func, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.note_const import PASSWORD_SCHEMES, make_readonly_name
from passlib.context import CryptContext
from app.note_const import (
    ALLOW_CHAR_IN_NAMES,
    DISABLE_WORDS_IN_NAMES,
    Metadata,
)
from app.utils import ensure_dir
from .base import DatabaseColumnBase, db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from app.config import Config

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
    user_accessed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), onupdate=func.now()
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
                > self.user_accessed_at + datetime.timedelta(seconds=self.timeout_seconds)
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


class MailAcceptStatus:
    ACCEPT = 1
    DENY = 2
    PENDING = 3
    NO_REQUESTED = 4  # 1. no in db; 2. in db but not requested / request timeout


class MailAddress(db.Model, DatabaseColumnBase):
    __tablename__ = "mail_addresses"

    address: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[int] = mapped_column(Integer, default=MailAcceptStatus.PENDING)


def verify_name(name: str) -> bool:
    if name in DISABLE_WORDS_IN_NAMES:
        return False
    if not 2 <= len(name) <= 50:
        return False
    if not all([c in ALLOW_CHAR_IN_NAMES for c in name]):
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
            readonly_name = make_readonly_name()
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
    ) -> Note:
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
        return note

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

    class FileAtDiskData(NamedTuple):
        file_path: str
        file_size: int

    def add_file(
        self, note: Note, filename: str, file_saver: Callable[[str], Any]
    ) -> File:
        file_data = self.add_file_at_disk(note, filename, file_saver)
        file = File(
            filename=filename,
            file_path=file_data.file_path,
            note=note,
            file_size=file_data.file_size,
        )
        self.session.add(file)
        note.all_file_size += file_data.file_size
        self.session.add(note)
        self.session.commit()
        return file

    def add_file_at_disk(
        self, note: Note, filename: str, file_saver: Callable[[str], Any]
    ) -> FileAtDiskData:
        filename_secured = secure_filename(
            "%s_%s_%s" % (time.time(), note.name, filename)
        )
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename_secured)
        ensure_dir(Config.UPLOAD_FOLDER)
        file_saver(file_path)
        file_size = os.path.getsize(file_path)
        return self.FileAtDiskData(file_path, file_size)

    def delete_file(self, file: File) -> None:
        file_path = file.file_path
        file.note.all_file_size -= file.file_size
        self.session.add(file.note)
        self.delete_file_at_disk(file_path)
        self.session.delete(file)
        self.session.commit()

    def delete_file_at_disk(self, file_path: str) -> None:
        try:
            os.remove(file_path)
        except:
            pass

    def get_file(self, file_id: int) -> Optional[File]:
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

    def on_user_access_note(self, note: Note) -> None:
        """
        Call when user successfully view the note via web,
        used to determine when should the note be removed.
        """
        note.user_accessed_at = func.now()
        self.session.add(note)
        self.session.commit()

    def set_mail_subscribe_setting(self, mail_address: str, status: int) -> None:
        mail = self.get_mail_address(mail_address)
        if mail is None:
            mail = MailAddress(address=mail_address)
        mail.status = status
        self.session.add(mail)
        self.session.commit()

    def get_mail_subscribe_setting(self, mail_address: str) -> int:
        mail = self.get_mail_address(mail_address)
        if mail is None:
            return MailAcceptStatus.NO_REQUESTED
        return mail.status

    def can_send_verification_normal_mail(self, mail_address: str) -> tuple[bool, bool]:
        """
        Determine if a mail can be sent to the address.
        Returns a tuple of two booleans:
        1. Whether a verification mail can be sent.
        2. Whether the address is already verified, i.e. can receive normal mails exported from Clip.
        """
        mail = self.get_mail_address(mail_address)
        if mail is None:
            # can send verification mail only
            return (True, False)

        if mail.status == MailAcceptStatus.PENDING:
            # check verify timeout, make PENDING to NO_REQUESTED
            if (
                mail.updated_at
                + datetime.timedelta(seconds=Metadata.mail_verify_timeout)
                < datetime.datetime.now()
            ):
                datastore.set_mail_subscribe_setting(
                    mail_address, MailAcceptStatus.NO_REQUESTED
                )
                # can send verification mail only, as previous timeout
                return (True, False)
            else:
                # can't send any mail
                return (False, False)
        return (
            mail.status in {MailAcceptStatus.ACCEPT, MailAcceptStatus.NO_REQUESTED},
            mail.status == MailAcceptStatus.ACCEPT,
        )

    def delete_mail_address(self, mail_address: str) -> None:
        mail = self.get_mail_address(mail_address)
        if mail is not None:
            self.session.delete(mail)
            self.session.commit()

    def get_mail_address(self, mail_address: str) -> Optional[MailAddress]:
        return self.session.query(MailAddress).filter_by(address=mail_address).first()


datastore = NoteDatastore(db)
