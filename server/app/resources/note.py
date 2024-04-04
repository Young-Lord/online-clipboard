import base64
import binascii
import datetime
import json
import os
from pathlib import Path
import re
import time
from flask_mailman import EmailMessage
from flask_restx import Resource, marshal
import functools
from typing import Any, ClassVar, Literal, Optional
from flask import (
    current_app,
    make_response,
    request,
    send_from_directory,
)
from flask_restx import Resource, fields
import jinja2
from app.config import Config
from app.models.datastore import (
    File,
    MailAcceptStatus,
    Note,
    datastore,
    combine_name_and_password,
    combine_name_and_password_and_readonly,
    verify_name,
    passlib_context,
)
from .base import api_restx as api, limiter, api_bp, api_restx_at_root
from app.note_const import READONLY_PREFIX, Metadata, ALLOW_CHAR_IN_NAMES
from app.utils import ensure_dir, return_json, sha256, sha512
from app.models.base import db
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


NO_DATA_METHODS = {"get", "options", "delete"}
LIMITER_METHODS = ["get", "post", "put", "delete"]
limiter_with_methods = functools.partial(limiter.limit, methods=LIMITER_METHODS)


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

        password: str = ""
        header_password = (
            request.headers.get("Authorization", "")
            .removeprefix("Bearer")
            .removeprefix(" ")
        )
        if header_password != "":
            # first, try get password from Authorization header
            try:
                password = base64.b64decode(header_password).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError):
                return return_json(status_code=400, message="Invalid password provided")
        else:
            # then, try get password from query string (first try "password", then try "pwd")
            plain_password = request.args.get("pwd", "")
            if plain_password != "":
                password = sha512(plain_password)

        name: str = kwargs.get("name", "")

        if (
            name.startswith(READONLY_PREFIX)
            and (note := datastore.get_note_by_readonly_name(name)) is not None
        ):
            # for encrypted read-only note, we must make sure user has the correct password
            # else we can simply return the note, bypassing the password check
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


def illegal_note_filter(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method.lower() == "options":
            return f(*args, **kwargs)
        name: str = kwargs.get("name", "")
        if name.startswith(READONLY_PREFIX):
            note = datastore.get_note_by_readonly_name(
                readonly_name=name,
            )
        else:
            note = datastore.get_note(
                name,
            )
        if note is None:
            # allow operate on non-exist note
            return f(*args, **kwargs)
        if note.ban_unitl is not None and note.ban_unitl > datetime.datetime.now():
            return return_json(status_code=451, message="Note is banned")
        return f(*args, **kwargs)

    return decorated_function


base_decorators = [  # this is fking from bottom to top!
    password_protected_note,
    illegal_note_filter,
    verify_name_decorator,
    verify_dict_decorator,
]


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
    return current_app.config["API_URL"] + "/file/%s/%s?jwt=%s" % (
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
        k: (
            v if k in ALLOW_PROPS else type(v)()
        )  # create object with default value (0 or empty)
        for k, v in ret.items()
    }
    ret = {**ret, **PROP_DEFAULT_VALUES}
    ret["is_readonly"] = True
    return return_json(ret, status_code=status_code)


class BaseRest(Resource):
    decorators = base_decorators

    def options(self, *args, **kwargs):
        return return_json(status_code=200)


note_limiter = limiter_with_methods(Metadata.limiter_note)
file_limiter = limiter_with_methods(Metadata.limiter_file)


@api.route("/note/<string:name>")
class NoteRest(BaseRest):
    decorators = [note_limiter] + base_decorators

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
            return return_json(status_code=400, message="Clip already exist")
        datastore.update_note(name=name)
        note = datastore.get_note(
            name,
        )
        assert note is not None
        return marshal_note(note, 201)

    def put(self, name: str):
        # update a note
        orig_params = request.get_json()
        # handle illegal note report
        if orig_params.get("report", False):
            note = datastore.get_note(name=name) or datastore.get_note_by_readonly_name(readonly_name=name)
            assert note is not None
            datastore.report_note(note)
            return return_json(status_code=200, message="Note reported")
        # otherwise, handle normal update
        if "new_password" in orig_params:
            orig_params["password"] = orig_params["new_password"]
        allow_props = [
            "content",
            "password",
            "clip_version",
            "timeout_seconds",
            "user_property",
            "enable_readonly",
        ]
        params = {k: v for k, v in orig_params.items() if k in allow_props}
        if len(params) == 0:
            return return_json(status_code=400, message="No property to update")
        content = params.get("content", "")
        user_property = params.get("user_property", "")
        if (
            len(content) > Metadata.max_content_length
            or len(user_property) > Metadata.max_user_property_length
        ):
            return return_json(status_code=400, message="Content too long")
        password = params.get("password", "")
        if len(password) > Metadata.max_password_length:
            return return_json(status_code=400, message="Password too long")
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        if "combine_mode" in orig_params:
            if orig_params["combine_mode"] == "prepend":
                params["content"] = content + note.content
            elif orig_params["combine_mode"] == "append":
                params["content"] = note.content + content
            else:
                return return_json(status_code=400, message="Invalid combine_mode")
            params.pop("combine_mode", None)
            params.pop("clip_version", None)
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


@api_restx_at_root.route("/raw/<string:name>")
class RawNoteRest(BaseRest):
    decorators = NoteRest.decorators

    def get(self, name: str):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        return make_response(
            note.content,
            200,
            {"Content-Type": "text/plain; charset=utf-8"},
        )


@api.route("/note/<string:name>/file/<int:id>")
class FileRest(BaseRest):
    decorators = [file_limiter] + base_decorators

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
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
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
    decorators = (
        [file_limiter]
        + [jwt_required(locations=["query_string"])]
        + [
            i
            for i in base_decorators
            if i not in {password_protected_note, verify_name_decorator}
        ]
    )
    as_attachment: ClassVar[bool] = True

    def get(self, id: int):
        return get_file(id, as_attachment=self.as_attachment)


@api.route("/file/<int:id>/preview")
class PreviewFileContentRest(DownloadFileContentRest):
    as_attachment = False


email_templates = jinja2.Environment(
    loader=jinja2.FileSystemLoader("app/mails"), autoescape=True
)


@api_bp.route("/mail/<string:address>/settings", methods=["GET"])
@limiter.limit("10/minute")
@jwt_required(locations=["query_string"])
def api_mail_setting(address: str):
    # validate JWT token
    if get_jwt_identity() != address:
        return return_json(status_code=403, message="Permission denied")

    # get mail subscribe setting from querystring
    if "subscribe" not in request.args:
        return return_json(status_code=400, message="No subscribe setting provided")
    arg_subscribe_str = request.args["subscribe"].lower()
    if arg_subscribe_str not in {"true", "false"}:
        return return_json(status_code=400, message="Invalid subscribe setting")

    status = (
        MailAcceptStatus.ACCEPT
        if arg_subscribe_str == "true"
        else MailAcceptStatus.DENY
    )
    datastore.set_mail_subscribe_setting(address, status)
    return return_json(status_code=200, message="OK")


def create_subscribe_link(address: str, subscribe: bool) -> str:
    return current_app.config["API_URL"] + "/mail/%s/settings?subscribe=%s&jwt=%s" % (
        address,
        "true" if subscribe else "false",
        create_access_token(
            identity=address,
            expires_delta=datetime.timedelta(seconds=Metadata.mail_verify_timeout),
        ),
    )


def check_email_valid(email: str) -> bool:
    if not 1 <= len(email) <= 255:
        # https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
        return False
    return re.fullmatch(r".+@.+\..+", email) is not None


@api_bp.route("/mailto", methods=["POST"])
@limiter.limit(Metadata.limiter_send_mail)
def api_send_mail():
    if not Metadata.allow_mail:
        return return_json(
            status_code=403,
            message="Mail not allowed on this server",
            error_id="MAIL_NOT_ALLOWED",
        )

    data = request.get_json()
    address = data.get("address", "")
    if not check_email_valid(address):
        return return_json(
            status_code=400, message="Invalid mail address", error_id="INVALID_ADDRESS"
        )
    content = request.get_json().get("content", "")
    if len(content) > Metadata.mail_max_content or content == "":
        return return_json(
            status_code=400, message="Invalid content", error_id="INVALID_CONTENT"
        )

    mail_address = datastore.get_mail_address(address)
    if mail_address is not None and mail_address.status == MailAcceptStatus.PENDING:
        # check verify timeout, make PENDING to NO_REQUESTED
        if (
            mail_address.updated_at
            + datetime.timedelta(seconds=Metadata.mail_verify_timeout)
            < datetime.datetime.now()
        ):
            datastore.set_mail_subscribe_setting(address, MailAcceptStatus.NO_REQUESTED)

    setting = datastore.get_mail_subscribe_setting(address)

    if setting == MailAcceptStatus.NO_REQUESTED:
        setting = MailAcceptStatus.PENDING
        msg = EmailMessage(
            subject="Clip - Confirm your mail address",
            body=email_templates.get_template("confirm_subscribe.jinja2").render(
                confirm_link=create_subscribe_link(address, True),
                unsubscribe_link=create_subscribe_link(address, False),
            ),
            to=[address],
        )
        msg.content_subtype = "html"
        msg.send()
        datastore.set_mail_subscribe_setting(address, setting)

    if setting in {
        MailAcceptStatus.NO_REQUESTED,
        MailAcceptStatus.PENDING,
        MailAcceptStatus.DENY,
    }:
        return return_json(
            status_code=202,
            message="Mail address must be verified",
            error_id="MAIL_NOT_VERIFIED",
        )
    assert setting == MailAcceptStatus.ACCEPT

    msg = EmailMessage(
        subject="Clip - Clip exported",
        body=email_templates.get_template("clip_content.jinja2").render(
            clip_url=current_app.config["HOMEPAGE_URL"],
            clip_content=content,
            unsubscribe_link=create_subscribe_link(address, False),
        ),
        to=[address],
    )
    msg.content_subtype = "html"
    msg.send()
    return return_json(status_code=200, message="OK")
