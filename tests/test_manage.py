import pytest
from app.db import get_db
from decouple import config

DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')

@pytest.mark.parametrize('path', (
    '/manage/menu',
    '/manage/test/profile',
    '/manage/test/create'
))
def test_manage_user(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 403


@pytest.mark.parametrize('label', (
    b'Manage',
    b'Id',
    b'Rol',
    b'test',
    b'DB_USER'
))
def test_menu_admin(client, auth, label):
    auth.login(username='DB_USER', password='DB_PASSWORD')
    assert client.get('/manage/menu').status_code == 200

    response = client.get('/manage/menu')
    assert label in response.data


def test_profile_admin(client, auth):
    auth.login(username='DB_USER', password='DB_PASSWORD')

    with client:
        assert client.get('/manage/holi1/profile').status_code == 200

        response = client.get('/manage/holi1/profile')
        assert b'Post Admin' in response.data
        assert b'by holi1 on\n                        2023-12-05' in response.data
        assert b'href="/4/update"' in response.data
        assert b'href="/manage/holi1/create"' in response.data
        assert b'New' in response.data
        assert b'edit' in response.data


def test_create_admin(client, auth, app):
    auth.login(username='DB_USER', password='DB_PASSWORD')

    response = client.get('/manage/holi1/create')

    assert client.get('/manage/holi1/create').status_code == 200
    assert b'Create Post' in response.data

    client.post(
        '/manage/holi1/create', data={
            'title': 'created_admin', 'body': 'holitas' 
            })
    
    with app.app_context():
        db = get_db()
        db.execute('SELECT COUNT(id) FROM post')
        count = db.fetchone()
        assert count['COUNT(id)'] == 4

        db.execute('SELECT id FROM flask.post WHERE title = "created_admin"')
        post_id = db.fetchone()
        assert client.post(f'/{post_id["id"]}/delete').status_code == 302

    
def test_create_update_validate(client, auth):
    auth.login(username='DB_USER', password='DB_PASSWORD')
    response = client.post('/manage/test/create', data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


@pytest.mark.parametrize('users', (
    'test',
    'a',
))
def test_detelete(client, auth, users, app):
    auth.login(username='DB_USER', password='DB_PASSWORD')

    assert client.post(f'manage/{users}/delete').status_code == 302

    client.post(f'manage/{users}/delete')

    with app.app_context():
        db = get_db()
        db.execute('SELECT username FROM flask.user WHERE username = %s', (users,))
        query = db.fetchone()
        assert query is None

