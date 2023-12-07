import pytest
from app.db import get_db


def test_create_post(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': 'body_test_for_test'})

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM post WHERE title = "created"')
        post = db.fetchone()
        assert post['title'] == 'created'


def test_index(client, auth, app):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'created' in response.data
    assert b'by test' in response.data
    assert b'body_test_for_test' in response.data


def test_update_user(client, auth, app):
    auth.login()

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM post WHERE title = "created"')
        post = db.fetchone()
    
    assert client.get(f'/{post["id"]}/update').status_code == 200
    client.post(f'/{post["id"]}/update', data={'title': 'Test_update', 'body': 'Test_body_update'})

    with app.app_context():
        db = get_db()
        db.execute(f'SELECT * FROM post WHERE id = {post["id"]}')
        post = db.fetchone()
        assert post['title'] == 'Test_update'
        assert post['body'] == 'Test_body_update'


@pytest.mark.parametrize('path', (
    '/update',
    '/delete',
))
def test_cheking_user(client, auth, path, app):
    auth.login(username='a', password='a')
    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM post WHERE title = "Test_update"')
        post = db.fetchone()
    assert client.get(f'/{post["id"]}'+path).status_code == 403


@pytest.mark.parametrize('path', (
    '/876/update',
    '/987/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create_update_validate(client, auth, app):
    auth.login()
    response = client.post('/create', data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM post WHERE title = "Test_update"')
        post = db.fetchone()

    response = client.post(f'/{post["id"]}/update', data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

    assert client.post(f'/{post["id"]}/delete').status_code == 302


def test_redirect(client):
    with client:
        response = client.get('/create')
        assert b'Redirecting...' in response.data


