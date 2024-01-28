import base64
import binascii
import datetime
import json
import os
from pathlib import Path
import time
from flask_restx import Resource, marshal
import functools
from typing import Any, ClassVar, Literal, Optional
from flask import (
    current_app,
    request,
    send_from_directory,
)
from flask_restx import Resource, fields
from app.config import Config
from app.models.datastore import (
    File,
    Note,
    datastore,
    combine_name_and_password,
    combine_name_and_password_and_readonly,
    verify_name,
    passlib_context,
)
from .base import api_restx as api
from app.note_const import READONLY_PREFIX, Metadata, ALLOW_CHAR_IN_NAMES
from app.utils import ensure_dir, return_json, sha256
from app.models.base import db
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


NO_DATA_METHODS = {"get", "options", "delete"}


def verify_dict_decorator(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method.lower() in NO_DATA_METHODS:
            return f(*args, **kwargs)
        if not (not request.is_json and request.form is not None):
            data: dict = (
                request.get_json()
            )  # this can raise HTTP 415 UNSUPPORTED MEDIA TYPE
            if not isinstance(data, dict):
                return return_json(status_code=400, message="Invalid data")
        return f(*args, **kwargs)

    return decorated_function


def verify_name_decorator(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        name: str = kwargs.get("name", "")
        if not verify_name(name) and not name.startswith(READONLY_PREFIX):
            return return_json(status_code=400, message="Invalid name")
        return f(*args, **kwargs)

    return decorated_function


def password_protected_note(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method.lower() == "options":
            return f(*args, **kwargs)
        password = (
            request.headers.get("Authorization", "")
            .removeprefix("Bearer")
            .removeprefix(" ")
        )
        if password != "":
            try:
                password = base64.b64decode(password).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError):
                return return_json(status_code=400, message="Invalid password provided")
        name: str = kwargs.get("name", "")

        if (
            name.startswith(READONLY_PREFIX)
            and (note := datastore.get_note_by_readonly_name(name)) is not None
        ):
            # for encrypted read-only note, we must make sure user has the password
            note_property = note.user_property
            try:
                prop_dict = json.loads(note_property)
            except json.JSONDecodeError:
                prop_dict = {}
            # check if encrypted
            if not prop_dict.get("encrypt_text_content", False):
                return f(*args, **kwargs)
            if not (prop_dict.get("encrypt_text_content_algo", "") == "aes"):
                return f(*args, **kwargs)
        else:
            note = datastore.get_note(
                name,
            )

        if note is None:
            # allow operate on non-exist note
            return f(*args, **kwargs)
            # return return_json(status_code=404, message="No note found")
        if note.password:
            valid, new_hash = passlib_context.verify_and_update(
                combine_name_and_password(note.name, password), note.password
            )
            if not valid:
                return return_json(status_code=401, message="Wrong password")
            if new_hash:
                note.password = new_hash
                datastore.session.add(note)
                datastore.session.commit()
        return f(*args, **kwargs)

    return decorated_function


def note_to_jwt_id(note: Note) -> str:
    return sha256(
        combine_name_and_password_and_readonly(
            note.name, note.password, note.readonly_name_if_has
        )
    )


def create_access_token_for_note(note: Note) -> str:
    return create_access_token(
        identity=note_to_jwt_id(note),
        expires_delta=datetime.timedelta(seconds=note.timeout_seconds),
    )


def verify_access_token_for_note(note: Note) -> bool:
    return get_jwt_identity() == note_to_jwt_id(note)


def create_file_link(file: File, suffix: Literal["download", "preview"]) -> str:
    return current_app.config["API_FULL_URL"] + "/file/%s/%s?jwt=%s" % (
        file.id,
        suffix,
        create_access_token_for_note(file.note),
    )


file_model = api.model(
    "File",
    {
        "filename": fields.String(attribute="filename"),
        "id": fields.Integer,
        "created_at": fields.DateTime,
        "timeout_seconds": fields.Integer,
        "expire_at": fields.DateTime(
            attribute=lambda file: file.created_at
            + datetime.timedelta(seconds=file.timeout_seconds)
        ),
        "download_url": fields.String(
            attribute=functools.partial(create_file_link, suffix="download")
        ),
        "preview_url": fields.String(
            attribute=functools.partial(create_file_link, suffix="preview")
        ),
        "size": fields.Integer(attribute="file_size"),
    },
)

note_model = api.model(
    "Note",
    {
        "name": fields.String,
        "content": fields.String,
        "clip_version": fields.Integer,
        "readonly_name": fields.String(
            attribute=lambda note: note.readonly_name_if_has
        ),
        "timeout_seconds": fields.Integer,
        "is_readonly": fields.Boolean(default=False),
        "files": fields.List(fields.Nested(file_model)),
        "file_count": fields.Integer(attribute=lambda note: len(note.files)),
        "all_file_size": fields.Integer,
        "user_property": fields.String,
    },
)


def marshal_note(note: Note, status_code: int = 200, message: Optional[str] = None):
    return return_json(
        marshal(note, note_model), status_code=status_code, message=message
    )


ALLOW_PROPS: list[str] = [
    "content",
    "readonly_name",
    "files",
    "all_file_size",
    "user_property",
]
PROP_DEFAULT_VALUES: dict[str, Any] = {}


def mashal_readonly_note(note: Note, status_code: int = 200):
    ret = marshal(note, note_model)
    assert isinstance(ret, dict)
    ret = {
        k: v
        if k in ALLOW_PROPS
        else type(v)()  # create object with default value (0 or empty)
        for k, v in ret.items()
    }
    ret = {**ret, **PROP_DEFAULT_VALUES}
    ret["is_readonly"] = True
    return return_json(ret, status_code=status_code)


base_decorators = [  # this is fking from bottom to top!
    password_protected_note,
    verify_name_decorator,
    verify_dict_decorator,
]


class BaseRest(Resource):
    decorators = base_decorators

    def options(self, *args, **kwargs):
        return return_json(status_code=200)


@api.route("/note/<string:name>")
class NoteRest(BaseRest):
    def get(self, name: str):
        if name.startswith(READONLY_PREFIX):
            note = datastore.get_note_by_readonly_name(
                readonly_name=name,
            )
            if note is None:
                return return_json(status_code=400, message="No note found")
            return mashal_readonly_note(note)
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=204, message="No note found")
        return marshal_note(note)

    def post(self, name: str):
        # create a new note
        note = datastore.get_note(
            name,
        )
        if note is not None:
            return return_json(status_code=400, message="Note already exist")
        datastore.update_note(name=name)
        note = datastore.get_note(
            name,
        )
        assert note is not None
        return marshal_note(note, 201)

    def put(self, name: str):
        params = request.get_json()
        if "new_password" in params:
            params["password"] = params["new_password"]
        allow_props = [
            "content",
            "password",
            "clip_version",
            "timeout_seconds",
            "user_property",
            "enable_readonly",
        ]
        params = {k: v for k, v in params.items() if k in allow_props}
        if len(params) == 0:
            return return_json(status_code=400, message="No property to update")
        content = params.get("content", "")
        user_property = params.get("user_property", "")
        if len(content) + len(user_property) > Metadata.max_content_length:
            return return_json(status_code=400, message="Content too long")
        password = params.get("password", "")
        if len(password) > Metadata.max_password_length:
            return return_json(status_code=400, message="Password too long")
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        try:
            datastore.update_note(name=name, **params)
        except ValueError as e:
            status_code = 400
            if str(e) == "clip_version too low":
                status_code = 409  # Conflict
            return marshal_note(note, status_code=status_code, message=str(e))
        return marshal_note(note)

    def delete(self, name: str):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        for file in note.files:
            datastore.delete_file(file)
        datastore.delete_note(note)
        return return_json(status_code=204, message="Note deleted")


@api.route("/note/<string:name>/file/<int:id>")
class FileRest(BaseRest):
    def get(self, name: str, id: int):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        file = datastore.get_file(id)
        if file is None:
            return return_json(status_code=404, message="No file found")
        return return_json(
            marshal(file, file_model),
            status_code=200,
        )

    def post(self, name: str, id: int):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        if len(note.files) >= Metadata.max_file_count:
            return return_json(
                status_code=400,
                message="Too many files",
                error_id="TOTAL_FILES_COUNT_LIMIT_HIT",
            )
        file = request.files.get("file")
        if file is None:
            return return_json(status_code=400, message="No file provided")
        if file.filename is None:
            return return_json(status_code=400, message="Filename is empty")

        # save file to local
        filename = secure_filename("%s_%s_%s" % (time.time(), name, file.filename))
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        ensure_dir(Config.UPLOAD_FOLDER)
        file.save(file_path)

        # check limits
        file_size = os.path.getsize(file_path)
        all_file_size_limit_hit = (
            file_size + note.all_file_size > Metadata.max_all_file_size
        )
        single_file_size_limit_hit = file_size > Metadata.max_file_size
        if all_file_size_limit_hit or single_file_size_limit_hit:
            os.remove(file_path)
            if all_file_size_limit_hit:
                message = "Too large all file size"
                error_id = "ALL_FILE_SIZE_LIMIT_HIT"
            else:
                message = "Too large file"
                error_id = "SINGLE_FILE_SIZE_LIMIT_HIT"
            return return_json(status_code=400, message=message, error_id=error_id)

        # add file to database
        datastore.add_file(note, file.filename, file_path, file_size)
        return return_json(status_code=201)

    def delete(self, name: str, id: int):
        file = datastore.get_file(id)
        if file is None:
            return return_json(status_code=404, message="No file found")
        datastore.delete_file(file)
        return return_json(status_code=204)


def get_file(id: int, as_attachment: bool):
    file = datastore.get_file(id)
    if file is None:
        return return_json(status_code=404, message="No file found")
    note = file.note
    if note is None:
        return return_json(status_code=404, message="No note found")
    if not verify_access_token_for_note(note):
        return return_json(status_code=403, message="Permission denied")
    file_path = Path(file.file_path).resolve()
    basepath = Path(Config.UPLOAD_FOLDER).resolve()
    relative_path = file_path.relative_to(basepath)
    try:
        return send_from_directory(
            directory=basepath,
            path=relative_path,
            as_attachment=as_attachment,
            download_name=file.filename,
        )
    except NotFound as e:
        return return_json(status_code=500, message="File not exist at server!")


@api.route("/file/<int:id>/download")
class DownloadFileContentRest(BaseRest):
    decorators = [jwt_required(locations=["query_string"])] + [
        i
        for i in base_decorators
        if i not in {password_protected_note, verify_name_decorator}
    ]
    as_attachment: ClassVar[bool] = True

    def get(self, id: int):
        return get_file(id, as_attachment=self.as_attachment)


@api.route("/file/<int:id>/preview")
class PreviewFileContentRest(DownloadFileContentRest):
    as_attachment = False
