from gevent import monkey
from gevent.pywsgi import WSGIServer
from app import create_app

monkey.patch_all()
app = create_app()

if __name__ == "__main__":
    # app.run()
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()
