from flask import Flask, Response
from werkzeug.middleware.proxy_fix import ProxyFix

from .factory import Factory
from app import models  # this must be imported to make migration work


def create_app(environment="development") -> Flask:
    f = Factory(
        environment,
    )
    f.set_flask()
    app = f.flask
    f.set_db()
    f.set_migration()
    with app.app_context():
        f.set_jwt()
        f.set_api()

    with app.app_context():
        from .views import frontend
        from .views import api

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(frontend, url_prefix="/")

    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore

    return app
