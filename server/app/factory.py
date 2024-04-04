import logging
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask

from .schedule_task import RemoveExpiredThings
from .note_const import Metadata
from .config import config, FLASK_ENV
from flask_cors import CORS


class Factory:
    flask: Flask

    def __init__(self):
        self._environment: str = FLASK_ENV

    @property
    def environment(self) -> str:
        return self._environment

    def set_flask(self, **kwargs):
        self.flask = Flask(__name__, **kwargs, static_folder=None, template_folder=None)
        self.flask.config.from_object(config)
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
            # from app.models.datastore import Datastore
            # Datastore(db).drop_it(yes_do_as_i_say=True)
            db.create_all()

    def set_migration(self):
        from .models.base import db, migrate

        migrate.init_app(self.flask, db)

    def set_cors(self):
        CORS(
            self.flask,
            origins=self.flask.config["CORS_ORIGINS"],
            allow_headers=["Content-Type", "Authorization"],
            supports_credentials=True,
            automatic_options=True,
        )

    def set_jwt(self):
        from .resources.base import file_jwt

        file_jwt.init_app(self.flask)

    def set_schedule_task(self):
        RemoveExpiredThings(self.flask)

    def set_rate_limit(self):
        from .resources.base import limiter

        limiter.init_app(self.flask)

    def set_mail(self):
        from .resources.base import mail

        mail.init_app(self.flask)
