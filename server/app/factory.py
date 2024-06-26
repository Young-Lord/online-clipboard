import logging
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask, Response, request

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

    def set_flask(self, **kwargs) -> Flask:
        self.flask = Flask(__name__, **kwargs, static_folder=None, template_folder=None)
        self.flask.config.from_object(config)

        return self.flask

    def set_logger(self) -> None:
        # setup logging
        file_handler = RotatingFileHandler("api.log", maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        self.flask.logger.addHandler(file_handler)
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(logging.DEBUG)
        self.flask.logger.addHandler(stdout)

    def set_db(self) -> None:
        from .models.base import db

        db.init_app(self.flask)
        with self.flask.app_context():
            # from app.models.datastore import Datastore
            # Datastore(db).drop_it(yes_do_as_i_say=True)
            db.create_all()

    def set_migration(self) -> None:
        from .models.base import db, migrate

        migrate.init_app(self.flask, db)

    def set_cors(self) -> None:
        CORS(
            self.flask,
            origins=self.flask.config["CORS_ORIGINS"],
            allow_headers=["Content-Type", "Authorization"],
            supports_credentials=True,
            automatic_options=True,
        )

        @self.flask.before_request
        def bypass_cors_requests():
            # fuck away non-200 CORS requests
            # many thanks to https://github.com/corydolphin/flask-cors/issues/292#issuecomment-883929183
            if request.method == "options" or request.method == "OPTIONS":
                return Response()
            # To create a slow-speed server: time.sleep(6)

    def set_jwt(self) -> None:
        from .resources.base import file_jwt

        file_jwt.init_app(self.flask)

    def set_schedule_task(self) -> None:
        RemoveExpiredThings(self.flask)

    def set_rate_limit(self) -> None:
        from .resources.base import limiter

        limiter.init_app(self.flask)

    def set_mail(self) -> None:
        from .resources.base import mail

        mail.init_app(self.flask)

    def set_socketio(self):
        with self.flask.app_context():
            from .resources.socketio import socketio

            socketio.init_app(self.flask)

    def set_csp(self) -> None:
        if self.flask.config["DEBUG"]:
            from .views.misc import csp_report

            self.flask.register_blueprint(
                csp_report, url_prefix=self.flask.config["API_SUFFIX"]
            )

        @self.flask.after_request
        def add_security_headers(resp: Response):
            # more strict CSP rule should be applied to untrusted files, i.e., user upload files
            if "Content-Security-Policy" not in resp.headers:
                resp.headers["Content-Security-Policy"] = " ".join(
                    [
                        "default-src 'self';",
                        "connect-src *;",
                        f"report-uri {self.flask.config['API_URL']}/csp-report;",
                        "style-src 'self' 'unsafe-inline';",
                    ]
                )
            return resp
