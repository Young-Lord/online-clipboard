from os import environ
from sys import argv
from app import create_app

if environ.get("VERCEL", "0") != "1":
    # need running server
    from gevent import monkey
    monkey.patch_all()
app = create_app()

from app.resources.socketio import socketio

# parse --debug arg
debug = "--debug" in argv[1:]

if __name__ == "__main__":
    print(
        f'[*] Listening on http://{app.config["BIND_HOST"]}:{app.config["BIND_PORT"]}'
    )
    # http_server = WSGIServer((app.config["BIND_HOST"], app.config["BIND_PORT"]), app)
    # http_server.serve_forever()
    socketio.run(app, host=app.config["BIND_HOST"], port=app.config["BIND_PORT"])
