import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from app.note_const import Metadata


class Config:
    SECRET_KEY: bytes = b"secret-key"  # used as JWT_SECRET_KEY

    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ERROR_404_HELP = False

    # upload stuff
    UPLOAD_FOLDER = "uploads"
    API_URL_SUFFIX = "/api"
    CORS_ORIGINS: list[str] = []
    MAX_CONTENT_LENGTH = Metadata.max_file_size

    DEBUG = False
    FRONTEND_URL: str = "http://192.168.1.8:5000"
    API_FULL_URL: str
    BIND_HOST = "127.0.0.1"
    BIND_PORT = 5000


class DevConfig(Config):
    FRONTEND_URL = "http://localhost:5000"
    CORS_ORIGINS = ["http://localhost:53000"]
    DEBUG = True


class ProdConfig(Config):
    BIND_HOST = "0.0.0.0"
    SECRET_KEY = os.environ.get("APP_SECRET", "").encode("ascii")
    assert (
        SECRET_KEY
    ), "APP_SECRET must be set.\nUse `python -c 'import secrets; print(secrets.token_urlsafe(128))'` to generate one."


config: dict[str, type[Config]] = {"development": DevConfig, "production": ProdConfig}
for v in config.values():
    v.API_FULL_URL = v.FRONTEND_URL + v.API_URL_SUFFIX
