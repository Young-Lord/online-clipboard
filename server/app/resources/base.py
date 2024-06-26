from typing import Any
from flask import Blueprint, current_app, make_response, request
from flask_jwt_extended import JWTManager
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_mailman import Mail
from flask_restx import Api, apidoc

from app.note_const import Metadata

SWAGGER_OPTIONS: dict[str, Any] = dict(doc=False, add_specs=False)
if current_app.config["DEBUG"] is True:
    SWAGGER_OPTIONS.pop("doc", None)
    SWAGGER_OPTIONS.pop("add_specs", None)

# this is the blueprint for normal API, usually at `/api` endpoint
api_bp = Blueprint("api", "api")
api_restx = Api(**SWAGGER_OPTIONS)
api_restx.init_app(api_bp)


@api_restx.documentation
def api_restx_documentation():
    response = make_response(apidoc.ui_for(api_restx))
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' data:;"
    )
    return response


# this is for special API such as `/raw`, usually at `/` endpoint
api_bp_at_root = Blueprint("api_at_root", "api_at_root")
api_restx_at_root = Api()
api_restx_at_root.init_app(api_bp_at_root, doc=False, add_specs=False)

# this is global JWT, but only used for file download now
file_jwt = JWTManager()


# this raises 429 error when rate limit in `app/note_const.py` exceeded
def RATELIMIT_DEFAULTS_EXEMPT_WHEN() -> bool:
    """
    Skip rate limit for specific requests
    """
    return False


limiter = Limiter(
    get_remote_address,
    default_limits=Metadata.limiter_default,
    default_limits_exempt_when=RATELIMIT_DEFAULTS_EXEMPT_WHEN,
)

# this is for sending mail, see https://flask-mailman.readthedocs.io/en/latest/
# and configure SMTP settings in `.env.production` file
mail = Mail()
