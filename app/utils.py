from functools import wraps

from flask import url_for, current_app, request, Response, Blueprint


def add_basic_auth(blueprint: Blueprint, username: str, password: str, realm: str='Api'):
    """
    Add HTTP Basic Auth to a blueprint.
    Note this is only for casual use!
    """

    @blueprint.before_request
    def basic_http_auth(*args, **kwargs):
        auth = request.authorization
        if auth is None or auth.password != password or auth.username != username:
            return Response('Please login', 401, {'WWW-Authenticate': f'Basic realm="{realm}"'})


def check_auth(username: str, password: str):
    """
    This function is called to check if a username /
    password combination is valid.
    """
    return username == current_app.config['DOC_USERNAME'] and password == current_app.config['DOC_PASSWORD']


def authenticate():
    """
    Sends a 401 response that enables basic auth
    """
    return Response('Not Authorized', 401, {'WWW-Authenticate': 'Basic realm="Api"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):  # type: ignore
            return authenticate()
        return f(*args, **kwargs)

    return decorated
