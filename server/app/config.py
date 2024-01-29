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
    MAX_CONTENT_LENGTH = Metadata.max_file_size

    # endpoint
    API_SUFFIX: str = os.environ["VITE_API_SUFFIX"]
    # _BASE_DOMAIN: str = os.environ["VITE_BASE_DOMAIN"]
    # _BASE_PATH: str = os.environ["VITE_BASE_PATH"]
    # FRONTEND_URL: str = os.environ["VITE_HOMEPAGE_BASEPATH"]
    API_FULL_URL: str = os.environ["VITE_API_ENDPOINT"]
    BIND_HOST = "127.0.0.1"
    BIND_PORT = 5000


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
