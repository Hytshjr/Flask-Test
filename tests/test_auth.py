import pytest
from app.db import get_db
from flask import g, session



def test_register(client, app, auth):
    with app.app_context():
        db = get_db()
        db.execute('INSERT INTO user (username, rol, password) VALUES ("test_admin", "admin", "scrypt:32768:8:1$McXgftRk5ESDHVgr$fa84e86cc52cb429096cb30a77eed852a876c1a24f4a5b7829d8bf9a1f255656448d7bb89d4a7ab1d14fe28a94cd3d213de1eb257195e79503ab4e6d5dbcde6a")')
        g.connect.commit()

    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"
    
    auth.register()


    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ) is not None

    
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


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        # assert session['user_id'] == 2
        assert g.user == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('jota', 'test', b'The username is incorrect.'),
    ('test', 'a', b'Your password is incorrect.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logged_checking(client, auth):

    auth.login()
    response = auth.login()
    with client:
        client.get('/auth/logi')
        assert response.headers["Location"] == "/"


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        print(session)
        assert session['user_id'] is None