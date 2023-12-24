import os

from app.note_const import Metadata


class Config:
    SECRET_KEY = os.getenv("APP_SECRET", "secret-key")

    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ERROR_404_HELP = False

    # upload stuff
    UPLOAD_FOLDER = "uploads"
    API_URL_SUFFIX = "/api"
    CORS_ORIGINS: list[str] = []
    MAX_CONTENT_LENGTH = Metadata.max_file_size

    DEBUG = False
    FRONTEND_URL = "http://192.168.1.8:5000"
    FRONTEND_URL: str
    API_FULL_URL: str


class DevConfig(Config):
    FRONTEND_URL = "http://localhost:5000"
    CORS_ORIGINS = ["http://localhost:53000"]
    DEBUG = True


class ProdConfig(Config):
    pass


config = {"development": DevConfig, "production": ProdConfig}
for v in config.values():
    v.API_FULL_URL = v.FRONTEND_URL + v.API_URL_SUFFIX
