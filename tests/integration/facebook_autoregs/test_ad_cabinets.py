from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest


@pytest.fixture
def ad_cabinet_name():
    return 'Muhammad ibn Musa al-Khwarizmi'


@pytest.fixture
def ad_cabinet_payload(ad_cabinet_name):
    return {
        'name': ad_cabinet_name,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def ad_cabinet(write_to_db, ad_cabinet_payload):
    return write_to_db('facebook_autoregs_ad_cabinet', ad_cabinet_payload)


def test_get_ad_cabinets(client, authorization, ad_cabinet, read_from_db):
    response = client.get('/api/v2/facebook/autoregs/ad-cabinets', headers={'Authorization': authorization})
    assert response.status_code == 200, response.text
    assert response.json == {
        'content': [{'id': ad_cabinet['id'], 'name': ad_cabinet['name']}],
        'pagination': {'page': 1, 'page_size': 20, 'sort_by': 'id', 'sort_order': 'asc', 'total': 1},
    }


def test_create_ad_cabinet(client, authorization, ad_cabinet_name, read_from_db):
    response = client.post(
        '/api/v2/facebook/autoregs/ad-cabinets',
        headers={'Authorization': authorization},
        json={'name': ad_cabinet_name},
    )
    assert response.status_code == 201, response.text

    db_payload = read_from_db('facebook_autoregs_ad_cabinet')
    assert db_payload == {'id': mock.ANY, 'created_at': mock.ANY, 'name': ad_cabinet_name}


def test_get_ad_cabinet(client, authorization, ad_cabinet):
    response = client.get(
        f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}',
        headers={'Authorization': authorization},
    )
    assert response.status_code == 200, response.text
    assert response.json == {'id': ad_cabinet['id'], 'name': ad_cabinet['name']}


def test_update_ad_cabinet(client, authorization, ad_cabinet, read_from_db):
    new_name = 'Ibn al-Haytham'
    assert ad_cabinet['name'] != new_name

    response = client.patch(
        f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}',
        headers={'Authorization': authorization},
        json={'name': new_name},
    )
    assert response.status_code == 200, response.text

    db_payload = read_from_db('facebook_autoregs_ad_cabinet', filters={'id': ad_cabinet['id']})
    assert db_payload == {'id': mock.ANY, 'created_at': mock.ANY, 'name': new_name}
