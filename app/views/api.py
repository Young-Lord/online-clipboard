from flask import Blueprint, jsonify, render_template, abort, request
from flask import send_from_directory
from app.models.datastore import NoteDatastore

from app.utils import return_json

api = Blueprint("api", "api")


@api.route("/version")
def api_version():
    return return_json(data={"version": "0.0.1"})


@api.route("/content/<name>")
def api_content(name: str):
    return return_json(
        data={"name": name, "content": f"This is the content for {name}."}
    )


@api.route("/update_content/<name>", methods=["POST"])
def api_update_content(name):
    content: str = request.get_json().get("content")
    if content is None:
        return return_json(status_code=400, message="No content provided")
    note = NoteDatastore(db).set_content(name, content)
    return return_json(data={"name": name, "content": note.content})
