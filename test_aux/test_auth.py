import pytest
from flask import g, session
from app.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

    
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )

    assert message in response.data


def test_register_checking(client, auth):
    with client:
        response = auth.register()
        assert b'Redirecting...' in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'The username is incorrect.'),
    ('test', 'a', b'Your password is incorrect.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logged_checking(client, auth):
    with client:
        response = auth.login()
        assert b'Redirecting...' in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        print(session)
        assert 'user_id' not in session