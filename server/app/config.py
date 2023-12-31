import os
from dotenv import load_dotenv
from app.note_const import Metadata

FLASK_ENV = os.environ.get("FLASK_ENV", "development")
load_dotenv(f"../.env.{FLASK_ENV}")
load_dotenv(f"../.env")


class Config:
    SECRET_KEY: bytes = b"secret-key"  # used as JWT_SECRET_KEY

    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ERROR_404_HELP = False

    # upload stuff
    UPLOAD_FOLDER = "uploads"
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS", ""
    ).split()  # separate consecutive whitespace, https://stackoverflow.com/a/46882411
    MAX_CONTENT_LENGTH = Metadata.max_file_size

    DEBUG = False
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
