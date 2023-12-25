import datetime
import os

from app.note_const import Metadata


class Config:
    SECRET_KEY = os.getenv("APP_SECRET", "secret-key")
    JWT_SECRET_KEY = SECRET_KEY

    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ERROR_404_HELP = False

    # upload stuff
    UPLOAD_FOLDER = "uploads"
    API_URL_SUFFIX = "/api"
    CORS_ORIGINS: list[str] = []
    MAX_CONTENT_LENGTH = Metadata.max_file_size
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        seconds=Metadata.file_link_timeout
    )  # Expire time -> 1 hour

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


config = {"development": DevConfig, "production": ProdConfig}
for v in config.values():
    v.API_FULL_URL = v.FRONTEND_URL + v.API_URL_SUFFIX
