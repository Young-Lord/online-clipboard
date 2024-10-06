from json import loads as json_loads
from os import environ
from typing import Any
from app.note_const import Metadata, FLASK_ENV


class Config:
    # basic
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ERROR_404_HELP = False

    # security
    SECRET_KEY: bytes = b"secret-key"  # used as JWT_SECRET_KEY
    CORS_ORIGINS: list[str] = environ.get(
        "CORS_ORIGINS", ""
    ).split()  # separate consecutive whitespace
    CORS_MAX_AGE = 7200  # cache CORS result for at most 2 hours

    # rate limit
    RATELIMIT_STORAGE_URI = "memory://"
    # set more at `note_const.py`

    # store - database
    SQLALCHEMY_DATABASE_URI: str = environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///main.db"
    )

    # store - upload
    UPLOAD_FOLDER = "uploads"
    # ensure file and text size are not too large
    MAX_CONTENT_LENGTH = max(
        Metadata.max_file_size,
        Metadata.max_content_length + Metadata.max_user_property_length + 500,
    )

    # endpoint
    API_SUFFIX = "/api"
    HOMEPAGE_URL: str = environ["VITE_HOMEPAGE_URL"]
    API_URL: str = environ["VITE_API_URL"]
    BIND_HOST: str = environ["BIND_HOST"]
    BIND_PORT: int = int(environ["BIND_PORT"])
    WEBSOCKET_PATH_FOR_SERVER = environ["WEBSOCKET_PATH_FOR_SERVER"]
    NO_FRONTEND: bool = (
        False  # set to True to disable frontend, only API will be available
    )
    BEHIND_REVERSE_PROXY: bool = environ["BEHIND_REVERSE_PROXY"] == "true"
    PROXYFIX_EXTRA_KWARGS: dict[str, Any] = json_loads(environ["PROXYFIX_EXTRA_KWARGS"] or "{}")

    # mail
    if Metadata.allow_mail:
        # https://waynerv.github.io/flask-mailman/
        MAIL_SERVER = environ.get("MAIL_SERVER", "localhost")
        MAIL_PORT = int(environ.get("MAIL_PORT", 25))
        MAIL_USERNAME = environ.get("MAIL_USERNAME", None)
        MAIL_PASSWORD = environ.get("MAIL_PASSWORD", None)
        MAIL_DEFAULT_SENDER = environ.get("MAIL_DEFAULT_SENDER", None)
        MAIL_USE_TLS = environ.get("MAIL_USE_TLS", "false").lower() == "true"
        MAIL_USE_SSL = environ.get("MAIL_USE_SSL", "false").lower() == "true"


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    BIND_HOST = "0.0.0.0"
    SECRET_KEY = environ.get("APP_SECRET", "").encode("ascii")
    assert (
        FLASK_ENV != "production" or SECRET_KEY
    ), 'APP_SECRET must be set.\nUse `python -c "import secrets; print(secrets.token_urlsafe(128))"` to generate one.'


configs: dict[str, type[Config]] = {"development": DevConfig, "production": ProdConfig}
config = configs[FLASK_ENV]
