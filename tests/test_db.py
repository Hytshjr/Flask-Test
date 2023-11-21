import pytest
import sqlite3
from app.db import get_db
from unittest.mock import patch


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('app.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_add_user_command(runner, monkeypatch, app):
    # Establecer la entrada simulada
    user_input = [
        'testuser',   # Usuario
        'admin',      # Rol
        'testpassword' # Contraseña
    ]

    with patch('builtins.input', side_effect=user_input):
        with app.app_context():
            result = runner.invoke(args=['user-db'])

            assert 'User add on the database.' in result.output


