from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .factory import Factory
from app import models  # this must be imported to make migration work  # type: ignore


def create_app() -> Flask:
    f = Factory()
    app = f.set_flask()
    f.set_logger()
    f.set_db()
    f.set_migration()
    f.set_cors()
    with app.app_context():
        f.set_jwt()
    f.set_rate_limit()
    f.set_mail()
    f.set_socketio()
    f.set_schedule_task()
    f.set_csp()

    from .views import frontend
    from .views import api_bp, api_bp_at_root

    app.register_blueprint(api_bp, url_prefix=app.config["API_SUFFIX"])
    # we must register frontend before api_bp_at_root, because the latter has a / route
    if not app.config["NO_FRONTEND"]:
        app.register_blueprint(frontend, url_prefix="/")
    app.register_blueprint(api_bp_at_root, url_prefix="/")

    if app.config["BEHIND_REVERSE_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, **app.config["PROXYFIX_EXTRA_KWARGS"])

    return app
