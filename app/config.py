import os

from app.note_const import Metadata


class Config:
    SECRET_KEY = os.getenv("APP_SECRET", "secret-key")

    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_URL = "http://localhost:3000"

    # upload stuff
    UPLOAD_FOLDER = "uploads"
    API_URL_SUFFIX = "/api"
    API_FULL_URL = FRONTEND_URL + API_URL_SUFFIX
    MAX_CONTENT_LENGTH = Metadata.max_file_size
    CORS_ORIGINS = ["http://localhost:53000"]


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


config = {"development": DevConfig, "production": ProdConfig}
