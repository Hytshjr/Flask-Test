import pytest
from app.db import get_db
from decouple import config


@pytest.mark.parametrize('path', (
    '/manage/menu',
    '/manage/test/profile',
    '/manage/test/create'
))
def test_manage_user(client, auth, path, app):
    auth.login()
    assert client.get(path).status_code == 403


@pytest.mark.parametrize('label', (
    b'Manage',
    b'Id',
    b'Rol',
    b'test',
    b'test_admin'
))
def test_menu_admin(client, auth, label):
    auth.login(username='test_admin', password='test')
    assert client.get('/manage/menu').status_code == 200

    response = client.get('/manage/menu')
    assert label in response.data


def test_create_admin(client, auth):
    auth.login(username='test_admin', password='test')
    response = client.get('/manage/test/create')

    assert client.get('/manage/test/create').status_code == 200
    assert b'Create Post' in response.data

    client.post(
        '/manage/test/create', data={
            'title': 'created_admin', 'body': 'holitas' 
            })
    

def test_profile_admin(client, auth, app):
    auth.login(username='test_admin', password='test')

    with client:
        response = client.get('/manage/test/profile')

        assert client.get('/manage/test/profile').status_code == 200
        assert b'created_admin' in response.data
        assert b'by test on\n' in response.data
        assert b'href="/manage/test/create"' in response.data
        assert b'New' in response.data
        assert b'edit' in response.data

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM post WHERE title = "created_admin"')
        post = db.fetchone()

        assert post['title'] == 'created_admin'
        assert client.post(f'/{post["id"]}/delete').status_code == 302

    
def test_create_update_validate(client, auth):
    auth.login(username='test_admin', password='test')
    response = client.post('/manage/test/create', data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


@pytest.mark.parametrize('users', (
    'test',
    'a',
))
def test_detelete(client, auth, users, app):
    auth.login(username='test_admin', password='test')

    assert client.post(f'manage/{users}/delete').status_code == 302

    client.post(f'manage/{users}/delete')

    with app.app_context():
        db = get_db()
        db.execute('SELECT username FROM user WHERE username = %s', (users,))
        query = db.fetchone()
        assert query is None


def test_delete_admin_user(client, auth, app):
    auth.login(username='test_admin', password='test')
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created_admim', 'body': 'body_test_for_test_admin'})

    with app.app_context():
        db = get_db()
        db.execute('SELECT * FROM post WHERE title = "created_admim"')
        post = db.fetchone()
        assert post['title'] == 'created_admim'

    assert client.post(f'/{post["id"]}/delete').status_code == 302
    client.post(f'/{post["id"]}/delete')

