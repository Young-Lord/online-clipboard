from gevent import monkey
from sys import argv
from app import create_app

monkey.patch_all()
app = create_app()

from app.resources.websocket import socketio

# parse --debug arg
debug = "--debug" in argv[1:]

if __name__ == "__main__":
    print(
        f'[*] Listening at http://{app.config["BIND_HOST"]}:{app.config["BIND_PORT"]}'
    )
    # http_server = WSGIServer((app.config["BIND_HOST"], app.config["BIND_PORT"]), app)
    # http_server.serve_forever()
    socketio.run(app, host=app.config["BIND_HOST"], port=app.config["BIND_PORT"], debug=debug)  # type: ignore (typeshed issue)
