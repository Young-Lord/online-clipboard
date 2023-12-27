from flask import Blueprint, render_template, abort
from flask import send_from_directory

templates_folder_name = "templates"
frontend = Blueprint(
    "frontend",
    "frontend",
    static_folder=f"app/{templates_folder_name}/static",
    template_folder=f"app/{templates_folder_name}",
)


@frontend.route("/")
def index():
    return render_template("index.html")


@frontend.route("/favicon.ico")
def favicon():
    return send_from_directory(
        templates_folder_name,
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@frontend.route("/<clip_name_input>")
def clip_name(clip_name_input):
    return render_template("index.html")
