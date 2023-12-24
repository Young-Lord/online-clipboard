import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask
from .note_const import Metadata
from .config import config


class Factory:
    flask: Flask

    def __init__(self, environment: str = "development"):
        self._environment: str = os.environ.get(
            "APP_ENVIRONMENT", os.environ.get("FLASK_ENV", environment)
        )

    @property
    def environment(self) -> str:
        return self._environment

    @environment.setter
    def environment(self, env: str):
        self._environment = env

    def set_flask(self, **kwargs):
        self.flask = Flask(__name__, **kwargs, static_folder=None, template_folder=None)
        self.flask.config.from_object(config[self._environment])
        # setup logging
        file_handler = RotatingFileHandler("api.log", maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        self.flask.logger.addHandler(file_handler)
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(logging.DEBUG)
        self.flask.logger.addHandler(stdout)

        return self.flask

    def set_db(self):
        from .models.base import db

        db.init_app(self.flask)
        with self.flask.app_context():
            db.create_all()

    def set_migration(self):
        from .models.base import db, migrate

        migrate.init_app(self.flask, db)

    def set_api(self):
        return
        # already registered as a blueprint
        from .resources.base import api_restx

        api_restx.init_app(
            self.flask,
            version=Metadata.version,
            title=Metadata.name,
            description=Metadata.description,
        )
