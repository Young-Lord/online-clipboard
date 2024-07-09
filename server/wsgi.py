from os import environ
from os.path import basename
from sys import argv


def parse_custom_args() -> None:
    from io import TextIOWrapper
    from argparse import ArgumentParser, FileType
    parser = ArgumentParser()
    parser.add_argument(
        "--export-metadata",
        help="Export metadata.json to file",
        type=FileType("w", encoding="UTF-8"),
        metavar="FILENAME",
    )
    parser.add_argument(
        "--export-openapi",
        help="Export openapi.json to file",
        type=FileType("w", encoding="UTF-8"),
        metavar="FILENAME",
    )
    args = parser.parse_args()
    export_metadata: TextIOWrapper = args.export_metadata
    export_openapi: TextIOWrapper = args.export_openapi
    no_run_server: bool = False

    if any((export_metadata, export_openapi)):
        no_run_server = True
        from json import dump

    if export_metadata:
        from app.note_const import Metadata_dict

        dump(Metadata_dict, export_metadata)

    if export_openapi:
        from app.main import create_app

        app = create_app()
        from app.resources.base import api_restx

        with app.app_context():
            dump(api_restx.__schema__, export_openapi, indent=4)

    if no_run_server:
        exit(0)


if basename(argv[0]) != "flask":
    # special case for running flask command
    parse_custom_args()

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
