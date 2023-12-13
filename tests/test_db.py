from app.db import get_db, close_db, create_db


def test_get_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_close_db(app):
    with app.app_context():
        close = close_db()
        assert close == None


def test_create_app(app):
    with app.app_context():
        create_test = create_db()
        assert create_test == 'The DB is already create.'

