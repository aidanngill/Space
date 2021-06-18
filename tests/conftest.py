import os
import pytest
import tempfile
from sqlalchemy import text

from space import create_app
from space.config import Testing
from space.extensions import db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as file:
    _data_sql = file.read().decode("utf-8")

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    upload_folder = tempfile.mkdtemp()

    class Configuration(Testing):
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path
        UPLOAD_FOLDER = upload_folder
        RECAPTCHA_ENABLED = False

    app = create_app(Configuration)

    with app.app_context():
        db.create_all()

        for statement in _data_sql.split(";"):
            db.engine.execute(text(statement + ";"))

    for file in ["owned-self.txt", "owned-other.txt", "anonymous.txt"]:
        with open(os.path.join(upload_folder, file), "w+"): pass

    yield app

    os.close(db_fd)
    os.unlink(db_path)

    for file in os.listdir(upload_folder):
        os.unlink(os.path.join(upload_folder, file))

    os.rmdir(upload_folder)

@pytest.fixture
def client(app):
    return app.test_client()
