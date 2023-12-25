from gevent import monkey
from gevent.pywsgi import WSGIServer
from app import create_app

monkey.patch_all()
app = create_app()

if __name__ == "__main__":
    # app.run()
    print(f'*Listeing at http://{app.config["BIND_HOST"]}:{app.config["BIND_PORT"]}')
    http_server = WSGIServer((app.config["BIND_HOST"], app.config["BIND_PORT"]), app)
    http_server.serve_forever()
