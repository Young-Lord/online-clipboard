from gevent import monkey
from app import create_app
from app.models.datastore import File, NoteDatastore
from app.models.base import db

monkey.patch_all()
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        store = NoteDatastore(db)
        test_name = "test"
        store.update_note(test_name, content="aaaa")
        test_note = store.get_note(test_name)
        assert test_note is not None
        print(test_note)
        store.add_file(test_note, "test.txt", "test", 100)
        test_note = store.get_note(test_name)
        assert test_note is not None
        print(test_note.files)
        print(store.get_file(list(test_note.files)[0].id))
        store.delete_file(test_note.files.pop())
        test_note = store.get_note(test_name)
        print(store.session.query(File).all())

    app.run()
