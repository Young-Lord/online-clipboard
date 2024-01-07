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


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
