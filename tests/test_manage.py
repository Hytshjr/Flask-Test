import pytest
from app.db import get_db


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
    b'other'
))
def test_menu_admin(client, auth, label):
    auth.login(username='other')
    assert client.get('/manage/menu').status_code == 200

    response = client.get('/manage/menu')
    assert label in response.data


def test_profile_admin(client, auth):
    auth.login(username='other')

    with client:
        assert client.get('/manage/test/profile').status_code == 200

        response = client.get('/manage/test/profile')
        print(response.data)
        assert b'test title' in response.data
        assert b'by test on\n                        2018-01-01' in response.data
        assert b'test\nbody' in response.data
        assert b'href="/1/update"' in response.data
        assert b'href="/manage/test/create"' in response.data
        assert b'New' in response.data
        assert b'edit' in response.data


def test_create_admin(client, auth, app):
    auth.login(username='other')

    response = client.get('/manage/test/create')

    assert client.get('/manage/test/create').status_code == 200
    assert b'Create Post' in response.data
    client.post(
        '/manage/test/create', data={
            'title_admin': 'test', 'body_admin': ''
            })

