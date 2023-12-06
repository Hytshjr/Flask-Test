import pytest
from app.db import get_db

def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'Post Admin' in response.data
    assert b'by holi1 on 2023-12-05' in response.data
    assert b'Post created for admin' in response.data
    assert b'"/10/update"' in response.data


def test_update_user(client, auth, app):
    auth.login()
    assert client.get('/10/update').status_code == 200
    client.post('/10/update', data={'title': 'Test update', 'body': 'Test body update'})

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM flask.post WHERE id = 10')
        post = db.fetchone()
        assert post['title'] == 'Test update'
        assert post['body'] == 'Test body update'

@pytest.mark.parametrize('path', (
    '/4/update',
    '/4/delete',
))
def test_cheking_user(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 403


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

@pytest.mark.parametrize('path', (
    '/create',
    '/10/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_create_post(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': 'Holitas'})

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM flask.post WHERE title = "created"')
        post = db.fetchone()
        assert post['title'] == 'created'

    auth.login()
    assert client.get(f'/{post["id"]}/update').status_code == 200
    assert client.get(f'/{post["id"]}/delete').status_code == 302

    with app.app_context():
        db = get_db()
        db.execute('SELECT id FROM flask.post WHERE title = "created"')
        post = db.fetchone()
        assert post == None


def test_redirect(client):
    with client:
        response = client.get('/create')
        assert b'Redirecting...' in response.data


