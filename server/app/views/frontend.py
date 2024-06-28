from pathlib import Path
from typing import Final
from flask import Blueprint, render_template, send_from_directory

templates_folders: Final[list[str]] = ["app/templates", "server/app/templates"]
templates_folder: Final[Path] = Path(
    next(i for i in templates_folders if Path(i).is_dir())
).absolute()
templates_folder_files: Final[set[str]] = set(i.name for i in templates_folder.iterdir() if i.is_file())
frontend = Blueprint(
    "frontend",
    "frontend",
    static_folder=templates_folder,
    static_url_path="/",
    template_folder=templates_folder,
)


@frontend.route("/")
def index():
    return render_template("index.html")


@frontend.route("/<clip_name_input>")
def clip_name(clip_name_input: str):
    if clip_name_input in templates_folder_files:
        return send_from_directory(templates_folder, clip_name_input)
    return render_template("index.html")
