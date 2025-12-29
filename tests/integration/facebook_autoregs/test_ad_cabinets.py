from unittest import mock

import pytest


class TestAdCabinet:
    def test_get_ad_cabinets(self, client, authorization, ad_cabinet, read_from_db):
        response = client.get('/api/v2/facebook/autoregs/ad-cabinets', headers={'Authorization': authorization})
        assert response.status_code == 200, response.text
        assert response.json == {
            'content': [
                {
                    'id': ad_cabinet['id'],
                    'name': ad_cabinet['name'],
                    'isBanned': ad_cabinet['is_banned'],
                    'businessManager': None,
                }
            ],
            'pagination': {'page': 1, 'page_size': 20, 'sort_by': 'id', 'sort_order': 'asc', 'total': 1},
        }

    def test_create_ad_cabinet(self, client, authorization, ad_cabinet_name, read_from_db):
        request_payload = {'name': ad_cabinet_name, 'isBanned': False}

        response = client.post(
            '/api/v2/facebook/autoregs/ad-cabinets',
            headers={'Authorization': authorization},
            json=request_payload,
        )
        assert response.status_code == 201, response.text
        assert response.json == {
            'id': mock.ANY,
            'name': request_payload['name'],
            'isBanned': request_payload['isBanned'],
            'businessManager': None,
        }

        db_payload = read_from_db('facebook_autoregs_ad_cabinet')
        assert db_payload == {
            'id': mock.ANY,
            'created_at': mock.ANY,
            'name': request_payload['name'],
            'is_banned': request_payload['isBanned'],
            'business_manager_id': None,
        }

    def test_get_ad_cabinet(self, client, authorization, ad_cabinet):
        response = client.get(
            f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 200, response.text
        assert response.json == {
            'id': ad_cabinet['id'],
            'name': ad_cabinet['name'],
            'isBanned': ad_cabinet['is_banned'],
            'businessManager': None,
        }

    def test_update_ad_cabinet(self, client, authorization, ad_cabinet, read_from_db):
        request_payload = {'name': 'Ibn al-Haytham', 'isBanned': True}
        assert ad_cabinet['name'] != request_payload['name']
        assert ad_cabinet['is_banned'] != request_payload['isBanned']

        response = client.patch(
            f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}',
            headers={'Authorization': authorization},
            json=request_payload,
        )
        assert response.status_code == 200, response.text
        assert response.json == {
            'id': mock.ANY,
            'isBanned': request_payload['isBanned'],
            'name': request_payload['name'],
            'businessManager': None,
        }

        db_payload = read_from_db('facebook_autoregs_ad_cabinet', filters={'id': ad_cabinet['id']})
        assert db_payload == {
            'id': mock.ANY,
            'created_at': mock.ANY,
            'name': request_payload['name'],
            'is_banned': request_payload['isBanned'],
            'business_manager_id': mock.ANY,
        }

    def test_bind_business_manager(self, client, authorization, ad_cabinet, business_manager, read_from_db):
        assert ad_cabinet['business_manager_id'] is None

        response = client.post(
            f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}/business-manager/{business_manager["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 201
        assert response.json == {
            'id': ad_cabinet['id'],
            'isBanned': ad_cabinet['is_banned'],
            'name': ad_cabinet['name'],
            'businessManager': {
                'id': business_manager['id'],
                'isBanned': business_manager['is_banned'],
                'name': business_manager['name'],
            },
        }

        db_payload = read_from_db('facebook_autoregs_ad_cabinet', filters={'id': ad_cabinet['id']})
        assert db_payload['business_manager_id'] == business_manager['id']


class TestAdCabinetWithBusinessManager:
    @pytest.fixture
    def ad_cabinet(self, business_manager, ad_cabinet_payload, write_to_db):
        return write_to_db(
            'facebook_autoregs_ad_cabinet', ad_cabinet_payload | {'business_manager_id': business_manager['id']}
        )

    def test_unbind_business_manager(self, client, authorization, ad_cabinet, business_manager, read_from_db):
        assert ad_cabinet['business_manager_id'] == business_manager['id']

        response = client.delete(
            f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}/business-manager/{business_manager["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 204

        db_payload = read_from_db('facebook_autoregs_ad_cabinet', filters={'id': ad_cabinet['id']})
        assert db_payload['business_manager_id'] is None

    def test_unbind_business_manager__nonexistent_business_manager(self, client, authorization, ad_cabinet):
        nonexistent_manager_id = 100500
        assert ad_cabinet['business_manager_id'] != nonexistent_manager_id

        response = client.delete(
            f'/api/v2/facebook/autoregs/ad-cabinets/{ad_cabinet["id"]}/business-manager/{nonexistent_manager_id}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 400
        assert response.json == {'message': 'Bad Business Manager'}
