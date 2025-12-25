from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest


@pytest.fixture
def executor_name():
    return 'Khalid ibn al-Walid'


@pytest.fixture
def executor_payload(executor_name):
    return {
        'name': executor_name,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def executor(write_to_db, executor_payload):
    return write_to_db('facebook_autoregs_executor', executor_payload)


def test_get_executors(client, authorization, executor, read_from_db):
    response = client.get('/api/v2/facebook/autoregs/executors', headers={'Authorization': authorization})
    assert response.status_code == 200, response.text
    assert response.json == {
        'content': [{'id': executor['id'], 'name': executor['name']}],
        'pagination': {'page': 1, 'page_size': 20, 'sort_by': 'id', 'sort_order': 'asc', 'total': 1},
    }


def test_create_executor(client, authorization, executor_name, read_from_db):
    response = client.post(
        '/api/v2/facebook/autoregs/executors', headers={'Authorization': authorization}, json={'name': executor_name}
    )
    assert response.status_code == 201, response.text

    db_payload = read_from_db('facebook_autoregs_executor')
    assert db_payload == {'id': mock.ANY, 'created_at': mock.ANY, 'name': executor_name}


def test_get_executor(client, authorization, executor):
    response = client.get(
        f'/api/v2/facebook/autoregs/executors/{executor["id"]}',
        headers={'Authorization': authorization},
    )
    assert response.status_code == 200, response.text
    assert response.json == {'id': executor['id'], 'name': executor['name']}


def test_update_executor(client, authorization, executor, read_from_db):
    new_name = 'Al-Malik al-Zahir Rukn al-Din Baybars al-Bunduqdari'
    assert executor['name'] != new_name

    response = client.patch(
        f'/api/v2/facebook/autoregs/executors/{executor["id"]}',
        headers={'Authorization': authorization},
        json={'name': new_name},
    )
    assert response.status_code == 200, response.text

    db_payload = read_from_db('facebook_autoregs_executor', filters={'id': executor['id']})
    assert db_payload == {'id': mock.ANY, 'created_at': mock.ANY, 'name': new_name}
