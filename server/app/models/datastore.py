from abc import ABC
import datetime
from enum import IntEnum
import json
import os
import secrets
import string
import time
from typing import Any, Callable, NamedTuple, Optional
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey, func, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.note_const import PASSWORD_SCHEMES, make_readonly_name
from passlib.context import CryptContext
from app.note_const import (
    ALLOW_CHAR_IN_NAMES,
    DISABLE_WORDS_IN_NAMES,
    BENEFIT_KEYS,
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
                > self.user_accessed_at
                + datetime.timedelta(seconds=self.timeout_seconds)
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
    user_property: Mapped[str] = mapped_column(
        String, default="{}", server_default="{}"
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


class MailAcceptStatus(IntEnum):
    ACCEPT = 1
    DENY = 2
    PENDING = 3
    NO_REQUESTED = 4  # 1. no in db; 2. in db but not requested / request timeout


class MailAddress(db.Model, DatabaseColumnBase):
    __tablename__ = "mail_addresses"

    address: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[int] = mapped_column(Integer, default=MailAcceptStatus.PENDING)


REDEEM_CODE_ALPHABET: str = string.ascii_uppercase + string.digits
REDEEM_CODE_LENGTH: int = 12


def make_redeem_code() -> str:
    return "".join(secrets.choice(REDEEM_CODE_ALPHABET) for _ in range(REDEEM_CODE_LENGTH))


def verify_redeem_code(code: str) -> bool:
    if not 4 <= len(code) <= 64:
        return False
    allowed = set(REDEEM_CODE_ALPHABET + "-_")
    return all(c in allowed for c in code)


class RedeemCode(db.Model, DatabaseColumnBase):
    """
    Admin-generated code that grants benefits when redeemed on a Note.
    `max_uses == -1` means unlimited; `valid_until is None` means no redeem deadline;
    `effect_duration_seconds == -1` means the granted effect lasts forever.
    """

    __tablename__ = "redeem_codes"

    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    note: Mapped[str] = mapped_column(
        String, nullable=False, default="", server_default=""
    )  # admin memo
    benefits: Mapped[str] = mapped_column(
        String, nullable=False, default="{}", server_default="{}"
    )  # JSON dict of benefits (keys subset of BENEFIT_KEYS)
    max_uses: Mapped[int] = mapped_column(
        Integer, nullable=False, default=-1, server_default=sql.expression.literal(-1)
    )
    used_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=sql.expression.literal(0)
    )
    valid_until: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )  # null = never expires for redeeming
    effect_duration_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=-1, server_default=sql.expression.literal(-1)
    )  # -1 means once redeemed, the effect lasts forever
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=sql.expression.true()
    )
    records: Mapped[list["RedeemRecord"]] = relationship(
        "RedeemRecord", back_populates="redeem_code"
    )

    @property
    def is_expired_for_redeem(self) -> bool:
        return (
            self.valid_until is not None and self.valid_until < datetime.datetime.now()
        )

    @property
    def is_used_up(self) -> bool:
        return self.max_uses != -1 and self.used_count >= self.max_uses

    @property
    def is_redeemable(self) -> bool:
        return (
            self.is_active and not self.is_expired_for_redeem and not self.is_used_up
        )

    @property
    def benefits_dict(self) -> dict[str, int]:
        try:
            parsed = json.loads(self.benefits or "{}")
        except (TypeError, ValueError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        return {k: int(v) for k, v in parsed.items() if k in BENEFIT_KEYS}

    def __repr__(self):
        return f"<RedeemCode {self.code}>"


class RedeemRecord(db.Model, DatabaseColumnBase):
    """A record of a redeem code being used by a particular note."""

    __tablename__ = "redeem_records"

    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"), nullable=False)
    redeem_code_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("redeem_codes.id"), nullable=False
    )
    benefits_snapshot: Mapped[str] = mapped_column(
        String, nullable=False, default="{}", server_default="{}"
    )
    activated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )  # null means never expires

    note: Mapped["Note"] = relationship("Note")
    redeem_code: Mapped["RedeemCode"] = relationship(
        "RedeemCode", back_populates="records"
    )

    @property
    def is_active(self) -> bool:
        return self.expires_at is None or self.expires_at > datetime.datetime.now()

    @property
    def benefits_dict(self) -> dict[str, int]:
        try:
            parsed = json.loads(self.benefits_snapshot or "{}")
        except (TypeError, ValueError):
            return {}
        if not isinstance(parsed, dict):
            return {}
        return {k: int(v) for k, v in parsed.items() if k in BENEFIT_KEYS}


def sanitize_benefits(raw: Any) -> dict[str, int]:
    """Filter benefit dict to known keys with non-negative integer values."""
    if not isinstance(raw, dict):
        return {}
    out: dict[str, int] = {}
    for key in BENEFIT_KEYS:
        if key not in raw:
            continue
        try:
            val = int(raw[key])
        except (TypeError, ValueError):
            continue
        if val < 0:
            continue
        out[key] = val
    return out


def merged_benefits_for_note(records: list["RedeemRecord"]) -> dict[str, int]:
    """Max-merge all active redeem records into a single benefits dict."""
    merged: dict[str, int] = {}
    for record in records:
        if not record.is_active:
            continue
        for k, v in record.benefits_dict.items():
            if k not in merged or v > merged[k]:
                merged[k] = v
    return merged


def effective_limits(note_records: list["RedeemRecord"]) -> dict[str, int]:
    """Default Metadata limits raised by any active redeem records."""
    base = {
        "max_file_size": Metadata.max_file_size,
        "max_file_count": Metadata.max_file_count,
        "max_all_file_size": Metadata.max_all_file_size,
        "max_timeout": Metadata.max_timeout,
    }
    for k, v in merged_benefits_for_note(note_records).items():
        if v > base.get(k, 0):
            base[k] = v
    return base


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


def verify_timeout_seconds(timeout_seconds: int, max_allowed: Optional[int] = None) -> bool:
    upper = Metadata.max_timeout if max_allowed is None else max(Metadata.max_timeout, max_allowed)
    return 1 <= timeout_seconds <= upper


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
        max_timeout_override: Optional[int] = None,
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
            # only allow increasing or equal clip_version (unless it is -1)
            if clip_version < note.clip_version and clip_version != -1:
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
            if not verify_timeout_seconds(timeout_seconds, max_allowed=max_timeout_override):
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
        # remove redeem records tied to this note
        self.session.query(RedeemRecord).filter_by(note_id=note.id).delete(
            synchronize_session=False
        )
        self.session.delete(note)
        self.session.commit()

    class FileAtDiskData(NamedTuple):
        file_path: str
        file_size: int

    def add_file(
        self,
        note: Note,
        filename: str,
        file_saver: Callable[[str], Any],
        user_property: str,
        timeout_seconds: Optional[int] = None,
    ) -> File:
        file_data = self.add_file_at_disk(note, filename, file_saver)
        kwargs: dict[str, Any] = dict(
            filename=filename,
            file_path=file_data.file_path,
            note=note,
            file_size=file_data.file_size,
            user_property=user_property,
        )
        if timeout_seconds is not None and timeout_seconds > 0:
            kwargs["timeout_seconds"] = timeout_seconds
        file = File(**kwargs)
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

    # ---------- Redeem code ----------

    def get_redeem_code(self, code_id: int) -> Optional[RedeemCode]:
        return self.session.query(RedeemCode).filter_by(id=code_id).first()

    def get_redeem_code_by_code(self, code: str) -> Optional[RedeemCode]:
        return self.session.query(RedeemCode).filter_by(code=code).first()

    def list_redeem_codes(
        self,
        query: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[RedeemCode], int]:
        q = self.session.query(RedeemCode)
        if query:
            like = f"%{query}%"
            q = q.filter(
                (RedeemCode.code.ilike(like)) | (RedeemCode.note.ilike(like))
            )
        total = q.count()
        rows = q.order_by(RedeemCode.id.desc()).limit(limit).offset(offset).all()
        return rows, total

    def create_redeem_code(
        self,
        *,
        code: Optional[str] = None,
        note: str = "",
        benefits: Optional[dict[str, int]] = None,
        max_uses: int = -1,
        valid_until: Optional[datetime.datetime] = None,
        effect_duration_seconds: int = -1,
    ) -> RedeemCode:
        if code is None or code == "":
            # generate a unique random code
            for _ in range(20):
                candidate = make_redeem_code()
                if self.get_redeem_code_by_code(candidate) is None:
                    code = candidate
                    break
            else:
                raise ValueError("Failed to generate a unique redeem code")
        else:
            if not verify_redeem_code(code):
                raise ValueError("Invalid code format")
            if self.get_redeem_code_by_code(code) is not None:
                raise ValueError("Code already exists")
        benefits_clean = sanitize_benefits(benefits or {})
        rc = RedeemCode(
            code=code,
            note=note or "",
            benefits=json.dumps(benefits_clean, sort_keys=True),
            max_uses=max_uses,
            used_count=0,
            valid_until=valid_until,
            effect_duration_seconds=effect_duration_seconds,
            is_active=True,
        )
        self.session.add(rc)
        self.session.commit()
        return rc

    def update_redeem_code(
        self,
        rc: RedeemCode,
        *,
        note: Optional[str] = None,
        benefits: Optional[dict[str, int]] = None,
        max_uses: Optional[int] = None,
        valid_until: Optional[Optional[datetime.datetime]] = None,
        effect_duration_seconds: Optional[int] = None,
        is_active: Optional[bool] = None,
        _set_valid_until: bool = False,
    ) -> RedeemCode:
        if note is not None:
            rc.note = note
        if benefits is not None:
            rc.benefits = json.dumps(sanitize_benefits(benefits), sort_keys=True)
        if max_uses is not None:
            rc.max_uses = max_uses
        if _set_valid_until:
            rc.valid_until = valid_until
        if effect_duration_seconds is not None:
            rc.effect_duration_seconds = effect_duration_seconds
        if is_active is not None:
            rc.is_active = is_active
        self.session.add(rc)
        self.session.commit()
        return rc

    def delete_redeem_code(self, rc: RedeemCode) -> None:
        # do NOT cascade-delete RedeemRecord; we keep history so a clip still
        # sees the benefits granted by codes that admins remove.
        # Set FK to NULL is not allowed (NOT NULL), so we delete records too,
        # but their benefits_snapshot has already been applied to the note via
        # active checks. The user's effect ends when their record is gone.
        self.session.query(RedeemRecord).filter_by(redeem_code_id=rc.id).delete(
            synchronize_session=False
        )
        self.session.delete(rc)
        self.session.commit()

    def get_active_records_for_note(self, note: Note) -> list[RedeemRecord]:
        rows = (
            self.session.query(RedeemRecord).filter_by(note_id=note.id).all()
        )
        return [r for r in rows if r.is_active]

    def get_records_for_note(self, note: Note) -> list[RedeemRecord]:
        return (
            self.session.query(RedeemRecord)
            .filter_by(note_id=note.id)
            .order_by(RedeemRecord.id.desc())
            .all()
        )

    def redeem_code_for_note(self, note: Note, code: str) -> RedeemRecord:
        """
        Apply a redeem code to a note, creating a RedeemRecord.
        Raises ValueError on common failures so callers can map to HTTP codes.
        """
        rc = self.get_redeem_code_by_code(code)
        if rc is None:
            raise ValueError("CODE_NOT_FOUND")
        if not rc.is_active:
            raise ValueError("CODE_INACTIVE")
        if rc.is_expired_for_redeem:
            raise ValueError("CODE_EXPIRED")
        if rc.is_used_up:
            raise ValueError("CODE_USED_UP")
        benefits = rc.benefits_dict
        if not benefits:
            raise ValueError("CODE_NO_BENEFITS")
        activated_at = datetime.datetime.now()
        if rc.effect_duration_seconds and rc.effect_duration_seconds > 0:
            expires_at: Optional[datetime.datetime] = (
                activated_at + datetime.timedelta(seconds=rc.effect_duration_seconds)
            )
        else:
            expires_at = None
        record = RedeemRecord(
            note_id=note.id,
            redeem_code_id=rc.id,
            benefits_snapshot=json.dumps(benefits, sort_keys=True),
            activated_at=activated_at,
            expires_at=expires_at,
        )
        rc.used_count += 1
        self.session.add(record)
        self.session.add(rc)
        self.session.commit()
        return record


datastore = NoteDatastore(db)
