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
    f.set_rate_limit()
    f.set_mail()
    f.set_schedule_task()

    with app.app_context():
        from .views import frontend
        from .views import api_bp, api_bp_at_root

    app.register_blueprint(api_bp, url_prefix=app.config["API_SUFFIX"])
    app.register_blueprint(api_bp_at_root, url_prefix="/")
    app.register_blueprint(frontend, url_prefix="/")

    # if your app is behind a proxy, modify this as https://werkzeug.palletsprojects.com/en/latest/middleware/proxy_fix/#werkzeug.middleware.proxy_fix.ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore

    return app
