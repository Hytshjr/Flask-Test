import pytest
from app.db import get_db

def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


def test_update_user(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': 'test_update'})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'
        assert post['body'] == 'test_update'

@pytest.mark.parametrize('path', (
    '/1/update',
    '/1/delete',
))
def test_cheking_user(client, auth, path):
    auth.login('user')
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
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_create_post(client, auth, app):
    auth.login('user')
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': 'Holitas'})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

    auth.login('other')
    assert client.get('/2/update').status_code == 200
    assert client.get('/2/delete').status_code == 302


    


def test_delete_post(client, auth, app):
    auth.login()
    assert client.post('/1/delete').status_code == 302
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 0
