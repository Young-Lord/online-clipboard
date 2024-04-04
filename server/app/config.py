import os
from dotenv import load_dotenv
from app.note_const import Metadata

FLASK_ENV = os.environ.get("FLASK_ENV", "development")
load_dotenv(f"../.env.{FLASK_ENV}", override=True)
load_dotenv(f"../.env", override=True)


class Config:
    # basic
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ERROR_404_HELP = False

    # security
    SECRET_KEY: bytes = b"secret-key"  # used as JWT_SECRET_KEY
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS", ""
    ).split()  # separate consecutive whitespace

    # rate limit
    RATELIMIT_STORAGE_URI = "memory://"
    # set more at `note_const.py`

    # store - database
    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"

    # store - upload
    UPLOAD_FOLDER = "uploads"
    # ensure file and text size are not too large
    MAX_CONTENT_LENGTH = max(
        Metadata.max_file_size,
        Metadata.max_content_length + Metadata.max_user_property_length + 500,
    )

    # endpoint
    API_SUFFIX = "/api"
    HOMEPAGE_URL: str = os.environ["VITE_HOMEPAGE_URL"]
    API_URL: str = os.environ["VITE_API_URL"]
    BIND_HOST = "127.0.0.1"
    BIND_PORT = 5000
    NO_FRONTEND: bool = (
        False  # set to True to disable frontend, only API will be available
    )
    # set to True if your app is behind a proxy, this helps to get real IP address
    # see: https://werkzeug.palletsprojects.com/en/latest/middleware/proxy_fix/#werkzeug.middleware.proxy_fix.ProxyFix
    BEHIND_REVERSE_PROXY: bool = False

    # mail
    if Metadata.allow_mail:
        # https://waynerv.github.io/flask-mailman/
        MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
        MAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
        MAIL_USERNAME = os.environ.get("MAIL_USERNAME", None)
        MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", None)
        MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", None)
        MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() == "true"
        MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    BIND_HOST = "0.0.0.0"
    SECRET_KEY = os.environ.get("APP_SECRET", "").encode("ascii")
    assert (
        FLASK_ENV != "production" or SECRET_KEY
    ), 'APP_SECRET must be set.\nUse `python -c "import secrets; print(secrets.token_urlsafe(128))"` to generate one.'


configs: dict[str, type[Config]] = {"development": DevConfig, "production": ProdConfig}
config = configs[FLASK_ENV]
