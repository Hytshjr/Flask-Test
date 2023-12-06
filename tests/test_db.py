from flask import g
from app.db import get_db, close_db


def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_close_db(app):
    with app.app_context():
        close = close_db()
        assert close == None

