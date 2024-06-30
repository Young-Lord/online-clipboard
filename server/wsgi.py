from io import TextIOWrapper
from os import environ
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--export-metadata",
    help="Export metadata.json to file",
    type=argparse.FileType("w", encoding="UTF-8"),
    metavar="FILENAME"
)
args = parser.parse_args()

export_file: TextIOWrapper = args.export_metadata
if export_file:
    from app.note_const import Metadata_dict
    import json

    json.dump(Metadata_dict, export_file)
    exit(0)


if environ.get("VERCEL", "0") != "1":
    # need running server
    from gevent import monkey

    monkey.patch_all()

from app.main import create_app
app = create_app()

from app.resources.socketio import socketio


if __name__ == "__main__":
    print(
        f'[*] Listening on http://{app.config["BIND_HOST"]}:{app.config["BIND_PORT"]}'
    )
    # http_server = WSGIServer((app.config["BIND_HOST"], app.config["BIND_PORT"]), app)
    # http_server.serve_forever()
    socketio.run(app, host=app.config["BIND_HOST"], port=app.config["BIND_PORT"])
