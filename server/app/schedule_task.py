import threading
import time
# these are patched by gevent, do not import only `sleep` or `Thread`.
from flask import Flask
import schedule
from app.models.datastore import Note, datastore


class RemoveExpiredThings:
    def __init__(self, app: Flask):
        self.app = app
        self.scheduler = schedule.Scheduler()
        self.job = self.scheduler.every().hour.do(self.remove_stuff)
        self.thread = threading.Thread(target=self._run, daemon=True)
        # print("starting scheduler")
        self.thread.start()

    def _run(self):
        while True:
            self.scheduler.run_pending()
            time.sleep(60 * 60)  # not precise, but ok in most cases

    def remove_stuff(self):
        # print("removing expired stuff")
        with self.app.app_context():
            for note in datastore.session.query(Note).all():
                if note.is_expired:
                    datastore.delete_note(note)
                    continue
                for file in note.files:
                    if file.is_expired:
                        datastore.delete_file(file)
