from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .factory import Factory
from app import models  # this must be imported to make migration work


def create_app() -> Flask:
    f = Factory()
    f.set_flask()
    app = f.flask
    f.set_db()
    f.set_migration()
    f.set_cors()
    with app.app_context():
        f.set_jwt()
        # f.set_api()
    f.set_schedule_task()

    with app.app_context():
        from .views import frontend
        from .views import api

    app.register_blueprint(api, url_prefix=app.config["API_SUFFIX"])
    app.register_blueprint(frontend, url_prefix="/")

    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore

    return app
