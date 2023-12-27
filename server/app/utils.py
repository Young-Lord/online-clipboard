import os
from typing import Any, Optional
from flask import (
    current_app,
    jsonify,
    make_response,
    Response,
)


def return_json(
    data: Optional[Any] = None,
    message: Optional[str] = None,
    status_code: int = 200,
    http_status_code: Optional[int] = None,
) -> Response:
    if http_status_code is None:
        http_status_code = status_code
    return make_response(
        jsonify({"status": status_code, "message": message, "data": data}),
        http_status_code,
    )


from flask_cors import cross_origin

cors_decorator = cross_origin(
    origins=current_app.config["CORS_ORIGINS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True,
    automatic_options=True,
)

default_value_for_types = {
    bool: False,
    int: 0,
    float: 0.0,
    str: "",
    list: [],
    dict: {},
    tuple: (),
    set: set(),
}


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
