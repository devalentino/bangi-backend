from unittest import mock

import pytest


class TestBusinessManager:
    def test_get_business_managers(self, client, authorization, business_manager, read_from_db):
        response = client.get('/api/v2/facebook/autoregs/business-managers', headers={'Authorization': authorization})
        assert response.status_code == 200, response.text
        assert response.json == {
            'content': [
                {
                    'id': business_manager['id'],
                    'name': business_manager['name'],
                    'isBanned': False,
                    'executors': [],
                    'adCabinets': [],
                }
            ],
            'pagination': {'page': 1, 'page_size': 20, 'sort_by': 'id', 'sort_order': 'asc', 'total': 1},
        }

    def test_create_business_manager(self, client, authorization, business_manager_name, read_from_db):
        request_payload = {'name': business_manager_name, 'isBanned': False}

        response = client.post(
            '/api/v2/facebook/autoregs/business-managers',
            headers={'Authorization': authorization},
            json=request_payload,
        )
        assert response.status_code == 201, response.text
        assert response.json == {
            'id': mock.ANY,
            'isBanned': request_payload['isBanned'],
            'name': request_payload['name'],
            'adCabinets': [],
            'executors': [],
        }

        db_payload = read_from_db('facebook_autoregs_business_manager')
        assert db_payload == {
            'id': mock.ANY,
            'name': request_payload['name'],
            'is_banned': request_payload['isBanned'],
            'created_at': mock.ANY,
        }

    def test_get_business_manager(self, client, authorization, business_manager):
        response = client.get(
            f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 200, response.text
        assert response.json == {
            'id': business_manager['id'],
            'name': business_manager['name'],
            'isBanned': business_manager['is_banned'],
            'adCabinets': [],
            'executors': [],
        }

    def test_update_business_manager(self, client, authorization, business_manager, read_from_db):
        request_payload = {'name': 'Umar ibn al-Khattab', 'isBanned': True}
        assert business_manager['name'] != request_payload['name']
        assert business_manager['is_banned'] != request_payload['isBanned']

        response = client.patch(
            f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}',
            headers={'Authorization': authorization},
            json=request_payload,
        )
        assert response.status_code == 200, response.text
        assert response.json == {
            'id': business_manager['id'],
            'isBanned': request_payload['isBanned'],
            'name': request_payload['name'],
            'adCabinets': mock.ANY,
            'executors': mock.ANY,
        }

        db_payload = read_from_db('facebook_autoregs_business_manager', filters={'id': business_manager['id']})
        assert db_payload == {
            'id': mock.ANY,
            'created_at': mock.ANY,
            'name': request_payload['name'],
            'is_banned': int(request_payload['isBanned']),
        }

    def test_bind_business_manager_with_executor(
        self, client, authorization, business_manager, executor, write_to_db, read_from_db
    ):
        response = client.post(
            f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}/executors/{executor["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 201
        assert response.json == {
            'id': business_manager['id'],
            'name': business_manager['name'],
            'isBanned': business_manager['is_banned'],
            'adCabinets': mock.ANY,
            'executors': [
                {'id': executor['id'], 'name': executor['name'], 'isBanned': executor['is_banned']}
            ],  # business manager has executor
        }

        db_payload = read_from_db(
            'facebook_autoregs_business_manager2executor',
            filters={'businessmanager_id': business_manager['id'], 'executor_id': executor['id']},
        )
        assert db_payload

    def test_unbind_business_manager_with_executor(
        self, client, authorization, business_manager, executor, write_to_db, read_from_db
    ):
        write_to_db(
            'facebook_autoregs_business_manager2executor',
            {'businessmanager_id': business_manager['id'], 'executor_id': executor['id']},
        )

        response = client.delete(
            f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}/executors/{executor["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 204

        db_payload = read_from_db(
            'facebook_autoregs_business_manager2executor',
            filters={'businessmanager_id': business_manager['id'], 'executor_id': executor['id']},
        )
        assert db_payload is None

    def test_unbind_business_manager_with_executor__non_existent_executor(
        self, client, authorization, business_manager, write_to_db, read_from_db
    ):
        non_existent_executor = 100500

        response = client.delete(
            f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}/executors/{non_existent_executor}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 404
        assert response.json == {'message': 'Executor does not exist'}


class TestBusinessManagerWithExecutorAndAdCabinet:
    @pytest.fixture
    def ad_cabinet(self, executor, business_manager, ad_cabinet_payload, write_to_db):
        ad_cabinet = write_to_db(
            'facebook_autoregs_ad_cabinet', ad_cabinet_payload | {'business_manager_id': business_manager['id']}
        )

        write_to_db(
            'facebook_autoregs_business_manager2executor',
            {'businessmanager_id': business_manager['id'], 'executor_id': executor['id']},
        )

        return ad_cabinet

    def test_get_business_manager(self, client, authorization, business_manager, executor, ad_cabinet, write_to_db):
        response = client.get(
            f'/api/v2/facebook/autoregs/business-managers/{business_manager["id"]}',
            headers={'Authorization': authorization},
        )
        assert response.status_code == 200, response.text
        assert response.json == {
            'id': business_manager['id'],
            'name': business_manager['name'],
            'isBanned': business_manager['is_banned'],
            'executors': [{'id': executor['id'], 'name': executor['name'], 'isBanned': executor['is_banned']}],
            'adCabinets': [
                {
                    'id': ad_cabinet['id'],
                    'name': ad_cabinet['name'],
                    'isBanned': ad_cabinet['is_banned'],
                    'businessManager': {
                        'id': business_manager['id'],
                        'isBanned': business_manager['is_banned'],
                        'name': business_manager['name'],
                    },
                }
            ],
        }
