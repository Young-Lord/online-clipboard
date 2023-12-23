import datetime
from flask_restx import Resource, marshal
import functools
from typing import Any, Final
from flask import Blueprint, jsonify, render_template, abort, request, send_file
from flask_restx import Resource, fields, marshal_with
from app.models.datastore import (
    Note,
    NoteDatastore,
    verify_name,
    verify_password_hash,
)
from .base import api_restx
from app.note_const import READONLY_PREFIX, Metadata, ALLOW_CHAR_IN_NAMES
from app.utils import cors_decorator, return_json, default_value_for_types
from app.models.base import db
from app.resources.base import api_restx as api

datastore = NoteDatastore(db)

NO_DATA_METHODS = {"get", "options", "delete"}
PASSWORD_FROM_PARAM_METHODS = {"get", "options", "delete"}


def verify_dict_decorator(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method.lower() in NO_DATA_METHODS:
            return f(*args, **kwargs)
        data: dict = request.get_json()
        if not isinstance(data, dict):
            return return_json(status_code=400, message="Invalid data")
        return f(*args, **kwargs)

    return decorated_function


def verify_name_decorator(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        name = kwargs.get("name", "")
        if not verify_name(name) and not name.startswith(READONLY_PREFIX):
            return return_json(status_code=400, message="Invalid name")
        return f(*args, **kwargs)

    return decorated_function


def password_protected_note(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method.lower() == "options":
            return f(*args, **kwargs)
        password = request.headers.get("X-Clip-Password", "")
        name = kwargs.get("name", "")
        note = datastore.get_note(
            name,
        )
        if note is None or request.method.lower() == "options":
            # allow operate on non-exist note
            return f(*args, **kwargs)
            # return return_json(status_code=404, message="No note found")
        if note.password is not None:
            if not verify_password_hash(note.password, password, name=name):
                return return_json(status_code=401, message="Wrong password")
        return f(*args, **kwargs)

    return decorated_function


def timeout_note_decorator(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        name = kwargs.get("name", "")
        note = datastore.get_note(
            name,
        )
        if note is not None:
            if note.timeout_seconds > 0:  # TODO: verify timeout!
                now = datetime.datetime.utcnow()
                delta = now - note.updated_at
                if delta.total_seconds() > note.timeout_seconds:
                    datastore.delete_note(
                        name,
                    )
        return f(*args, **kwargs)

    return decorated_function


note_model = api.model(
    "Note",
    {
        "name": fields.String,
        "content": fields.String,
        "clip_version": fields.Integer,
        "readonly_name": fields.String,
        "timeout_seconds": fields.Integer,
        "is_readonly": fields.Boolean(default=False),
    },
)


def marshal_note(note: Note, status_code: int = 200):
    return return_json(marshal(note, note_model), status_code=status_code)


def mashal_readonly_note(note: Note, status_code: int = 200):
    ret = marshal(note, note_model)
    allow_props = ["content", "readonly_name"]
    assert isinstance(ret, dict)
    ret = {
        k: v if k in allow_props else default_value_for_types[type(v)]
        for k, v in ret.items()
    }
    ret["is_readonly"] = True
    return return_json(ret, status_code=status_code)


@api.route("/note/<string:name>")
class NoteRest(Resource):
    decorators = [  # this is fking from bottom to top!
        password_protected_note,
        verify_name_decorator,
        verify_dict_decorator,
        timeout_note_decorator,
        cors_decorator,
    ]

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
        if params.get("new_password"):
            params["password"] = params["new_password"]
        allow_props = ["content", "password", "clip_version", "timeout_seconds"]
        params = {k: v for k, v in params.items() if k in allow_props}
        if len(params) == 0:
            return return_json(status_code=400, message="No property to update")
        content = params.get("content", "")
        if len(content) > Metadata.max_content_length:
            return return_json(status_code=400, message="Content too long")
        password = params.get("password", "")
        if len(password) > Metadata.max_password_length:
            return return_json(status_code=400, message="Password too long")
        try:
            datastore.update_note(name=name, **params)
        except ValueError as e:
            return return_json(status_code=400, message=str(e))
        note = datastore.get_note(
            name,
        )
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        return marshal_note(note)

    def delete(self, name: str):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        datastore.delete_note(name)
        return return_json(status_code=204, message="Note deleted")

    def options(self, name: str):
        return return_json(status_code=200)


@api.route("/note/<string:name>/file/<int:id>")
class FileRest(Resource):
    decorators = [
        password_protected_note,
        verify_name_decorator,
        verify_dict_decorator,
        timeout_note_decorator,
        cors_decorator,
    ]

    def get(self, name: str, id: int):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        file = datastore.get_file(id)
        if file is None:
            return return_json(status_code=404, message="No file found")
        return send_file(file)

    def post(self, name: str, id: int):
        note = datastore.get_note(
            name,
        )
        if note is None:
            return return_json(status_code=404, message="No note found")
        file = request.files.get("file")
        if file is None:
            return return_json(status_code=400, message="No file provided")
        if file.filename is None:
            return return_json(status_code=400, message="Filename is empty")
        datastore.add_file(note, file.filename)
        return return_json(status_code=201)
