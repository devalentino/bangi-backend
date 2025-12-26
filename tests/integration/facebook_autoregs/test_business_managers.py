from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest


@pytest.fixture
def business_manager_name():
    return 'Abd Allah ibn Abi Quhafa'


@pytest.fixture
def business_manager_payload(business_manager_name):
    return {
        'name': business_manager_name,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def business_manager(write_to_db, business_manager_payload):
    return write_to_db('facebook_autoregs_business_manager', business_manager_payload)


def test_get_business_managers(client, authorization, business_manager, read_from_db):
    response = client.get('/api/v2/facebook/autoregs/business-managers', headers={'Authorization': authorization})
    assert response.status_code == 200, response.text
    assert response.json == {
        'content': [{'id': business_manager['id'], 'name': business_manager['name']}],
        'pagination': {'page': 1, 'page_size': 20, 'sort_by': 'id', 'sort_order': 'asc', 'total': 1},
    }


def test_create_business_manager(client, authorization, business_manager_name, read_from_db):
    response = client.post(
        '/api/v2/facebook/autoregs/business-managers',
        headers={'Authorization': authorization},
        json={'name': business_manager_name},
    )
    assert response.status_code == 201, response.text

    db_payload = read_from_db('facebook_autoregs_business_manager')
    assert db_payload == {'id': mock.ANY, 'created_at': mock.ANY, 'name': business_manager_name}


def test_get_business_manager(client, authorization, business_manager):
    response = client.get(
        f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}',
        headers={'Authorization': authorization},
    )
    assert response.status_code == 200, response.text
    assert response.json == {'id': business_manager['id'], 'name': business_manager['name']}


def test_update_business_manager(client, authorization, business_manager, read_from_db):
    new_name = 'Umar ibn al-Khattab'
    assert business_manager['name'] != new_name

    response = client.patch(
        f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}',
        headers={'Authorization': authorization},
        json={'name': new_name},
    )
    assert response.status_code == 200, response.text

    db_payload = read_from_db('facebook_autoregs_business_manager', filters={'id': business_manager['id']})
    assert db_payload == {'id': mock.ANY, 'created_at': mock.ANY, 'name': new_name}
