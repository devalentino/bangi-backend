from decimal import Decimal
from unittest import mock

import pytest


def test_create_campaign(client, authorization, campaign_payload, read_from_db):
    campaigns = read_from_db('campaign', fetchall=True)
    assert len(campaigns) == 0

    request_payload = {
        'name': campaign_payload['name'],
        'costModel': campaign_payload['cost_model'],
        'costValue': campaign_payload['cost_value'],
        'currency': campaign_payload['currency'],
    }

    response = client.post('/api/v2/core/campaigns', headers={'Authorization': authorization}, json=request_payload)

    assert response.status_code == 201, response.text

    campaign = read_from_db('campaign')
    assert campaign == {
        'id': mock.ANY,
        'name': request_payload['name'],
        'cost_model': request_payload['costModel'],
        'cost_value': request_payload['costValue'],
        'currency': request_payload['currency'],
        'created_at': mock.ANY,
    }


def test_campaigns_list(client, authorization, campaign_payload, write_to_db):
    for ci in range(25):
        write_to_db('campaign', {'name': f'Campaign {ci}', 'cost_model': 'cpm', 'cost_value': 1, 'currency': 'usd'})

    response = client.get('/api/v2/core/campaigns', headers={'Authorization': authorization})
    assert response.status_code == 200, response.text
    assert response.json == {
        'content': [
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 1, 'name': 'Campaign 0'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 2, 'name': 'Campaign 1'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 3, 'name': 'Campaign 2'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 4, 'name': 'Campaign 3'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 5, 'name': 'Campaign 4'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 6, 'name': 'Campaign 5'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 7, 'name': 'Campaign 6'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 8, 'name': 'Campaign 7'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 9, 'name': 'Campaign 8'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 10, 'name': 'Campaign 9'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 11, 'name': 'Campaign 10'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 12, 'name': 'Campaign 11'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 13, 'name': 'Campaign 12'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 14, 'name': 'Campaign 13'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 15, 'name': 'Campaign 14'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 16, 'name': 'Campaign 15'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 17, 'name': 'Campaign 16'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 18, 'name': 'Campaign 17'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 19, 'name': 'Campaign 18'},
            {'costModel': 'cpm', 'costValue': '1.00', 'currency': 'usd', 'id': 20, 'name': 'Campaign 19'},
        ],
        'pagination': {'page': 1, 'page_size': 20, 'sort_by': 'id', 'sort_order': 'asc', 'total': 25},
    }


def test_get_campaign(client, authorization, campaign):
    response = client.get(f'/api/v2/core/campaigns/{campaign["id"]}', headers={'Authorization': authorization})

    assert response.status_code == 200, response.text
    assert response.json == {
        'id': campaign['id'],
        'name': campaign['name'],
        'costModel': campaign['cost_model'],
        'costValue': str(campaign['cost_value'].quantize(Decimal('0.01'))),
        'currency': campaign['currency'],
    }


@pytest.mark.parametrize(
    'request_key,db_key,request_value',
    [
        ('name', 'name', 'Campaign updated'),
        ('costModel', 'cost_model', 'cpc'),
        ('costValue', 'cost_value', 11.50),
        ('currency', 'currency', 'eur'),
    ],
)
def test_update_campaign(client, authorization, campaign, read_from_db, request_key, db_key, request_value):
    assert campaign[db_key] != request_value

    response = client.patch(
        f'/api/v2/core/campaigns/{campaign["id"]}',
        headers={'Authorization': authorization},
        json={request_key: request_value},
    )

    assert response.status_code == 200, response.text

    campaign = read_from_db('campaign')
    assert campaign[db_key] == request_value
