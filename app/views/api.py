from flask import Blueprint, jsonify, render_template, abort, request
from flask import send_from_directory
from app.models.datastore import NoteDatastore, verify_password_hash

from app.utils import return_json
from app.models.database import db

api = Blueprint("api", "api")
datastore = NoteDatastore(db)


@api.route("/version")
def api_version():
    return return_json(data={"version": "0.0.1"})


@api.route("/content/<name>")
def api_content(name: str):
    password = request.args.get("password", "")
    note = datastore.get_note(
        name,
    )
    if note is None:
        return return_json(status_code=404, message="No note found")
    if note.password is not None:
        if not verify_password_hash(note.password, password, name=name):  # type: ignore
            return return_json(status_code=401, message="Wrong password")
    return return_json(data={"name": name, "content": note.content})


@api.route("/update_content/<name>", methods=["POST"])
def api_update_content(name):
    password = request.form.get("password", "")
    new_password = request.form.get("new_password", None)
    content = request.form.get("content", "")
    clip_version = int(request.form.get("clip_version", 1))
    note = datastore.get_note(
        name,
    )
    if note is None:
        datastore.update_note(
            name=name, password=password, content=content, clip_version=clip_version
        )
        note = datastore.get_note(
            name,
        )
        assert note is not None
    if note.password is not None:
        if not verify_password_hash(note.password, password, name=name):  # type: ignore
            return return_json(status_code=401, message="Wrong password")
    datastore.update_note(
        name=name,
        content=content,
        clip_version=clip_version,
    )
    if new_password is not None:
        datastore.update_note(
            name=name,
            password=new_password,
            clip_version=clip_version,
        )
    return return_json(data={"name": name, "content": note.content})
