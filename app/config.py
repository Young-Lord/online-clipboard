import os

class Config:
    ERROR_404_HELP = False

    SECRET_KEY = os.getenv("APP_SECRET", "secret-key")

    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DOC_USERNAME = "api"
    DOC_PASSWORD = "password"

    FRONTEND_URL = "http://localhost:3000"
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 512 * 1024 * 1024  # 512 MiB

class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


config = {"development": DevConfig, "production": ProdConfig}
