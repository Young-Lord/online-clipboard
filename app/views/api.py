from flask import Blueprint, render_template, abort
from flask import send_from_directory

api = Blueprint("api", "api")


@api.route("/content/<name>")
def api_content(name: str):
    return f"test content for {name}."


@api.route("/version")
def api_version():
    return "1.0.0"
