import io
import pathlib
import zipfile
from unittest import mock

import pytest


def _zip_bytes():
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as zip_file:
        zip_file.writestr('index.html', '<html></html>')
    archive.seek(0)
    return archive


@pytest.fixture
def flow(write_to_db, campaign):
    return write_to_db(
        'flow',
        {
            'campaign_id': campaign['id'],
            'order_value': 1,
            'action_type': 'redirect',
            'redirect_url': 'https://example.com',
            'landing_path': None,
            'is_enabled': True,
            'is_deleted': False,
        },
    )


def test_create_flow__redirect_action_success(client, authorization, campaign, read_from_db):
    request_payload = {
        'campaignId': campaign['id'],
        'orderValue': 1,
        'actionType': 'redirect',
        'redirectUrl': 'https://example.com',
        'isEnabled': True,
    }

    response = client.post(
        '/api/v2/core/flows',
        headers={'Authorization': authorization},
        data=request_payload,
        content_type='multipart/form-data',
    )

    assert response.status_code == 201, response.text

    flow = read_from_db('flow')
    assert flow == {
        'id': mock.ANY,
        'created_at': mock.ANY,
        'campaign_id': request_payload['campaignId'],
        'order_value': request_payload['orderValue'],
        'action_type': request_payload['actionType'],
        'redirect_url': request_payload['redirectUrl'],
        'landing_path': None,
        'is_enabled': request_payload['isEnabled'],
        'is_deleted': False,
    }


def test_create_flow__include_action_success(
    client, authorization, campaign, environment, read_from_db, landing_pages_base_path
):
    request_payload = {
        'campaignId': campaign['id'],
        'orderValue': 2,
        'actionType': 'include',
        'landingArchive': (_zip_bytes(), 'landing.zip'),
    }

    response = client.post(
        '/api/v2/core/flows',
        headers={'Authorization': authorization},
        data=request_payload,
        content_type='multipart/form-data',
    )

    assert response.status_code == 201, response.text

    flow = read_from_db('flow')
    expected_landing_path = str(pathlib.Path(landing_pages_base_path) / str(flow['id']))
    assert flow == {
        'id': mock.ANY,
        'created_at': mock.ANY,
        'campaign_id': request_payload['campaignId'],
        'order_value': request_payload['orderValue'],
        'action_type': request_payload['actionType'],
        'redirect_url': None,
        'landing_path': expected_landing_path,
        'is_enabled': 1,
        'is_deleted': 0,
    }
    assert (pathlib.Path(flow['landing_path']) / 'index.html').exists()


def test_create_flow__requires_redirect_url_for_redirect_action(client, authorization, campaign):
    response = client.post(
        '/api/v2/core/flows',
        headers={'Authorization': authorization},
        data={
            'campaignId': campaign['id'],
            'orderValue': 1,
            'actionType': 'redirect',
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 422, response.text
    assert response.json == {
        'code': 422,
        'errors': {'form': {'redirectUrl': ['redirectUrl is required for redirect action.']}},
        'status': 'Unprocessable Entity',
    }


def test_create_flow__requires_landing_archive_for_include_action(client, authorization, campaign):
    response = client.post(
        '/api/v2/core/flows',
        headers={'Authorization': authorization},
        data={
            'campaignId': campaign['id'],
            'orderValue': 1,
            'actionType': 'include',
            'redirectUrl': 'https://example.com',
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 422, response.text
    assert response.json == {
        'code': 422,
        'errors': {'form': {'landingArchive': ['landingArchive is required for include action.']}},
        'status': 'Unprocessable Entity',
    }


def test_create_flow__rejects_non_zip_landing_archive(client, authorization, campaign):
    response = client.post(
        '/api/v2/core/flows',
        headers={'Authorization': authorization},
        data={
            'campaignId': campaign['id'],
            'orderValue': 1,
            'actionType': 'include',
            'landingArchive': (io.BytesIO(b'not-a-zip'), 'landing.txt'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 422, response.text
    assert response.json == {
        'code': 422,
        'errors': {'form': {'landingArchive': ['landingArchive must be a .zip file.']}},
        'status': 'Unprocessable Entity',
    }


def test_update_flow__redirect_action_success(client, authorization, flow, read_from_db):
    request_payload = {
        'orderValue': 3,
        'actionType': 'redirect',
        'redirectUrl': 'https://example.org',
        'isEnabled': False,
    }

    response = client.patch(
        f'/api/v2/core/flows/{flow["id"]}',
        headers={'Authorization': authorization},
        data=request_payload,
        content_type='multipart/form-data',
    )

    assert response.status_code == 200, response.text

    updated = read_from_db('flow')
    assert updated == {
        'id': flow['id'],
        'created_at': mock.ANY,
        'campaign_id': flow['campaign_id'],
        'order_value': request_payload['orderValue'],
        'action_type': request_payload['actionType'],
        'redirect_url': request_payload['redirectUrl'],
        'landing_path': None,
        'is_enabled': request_payload['isEnabled'],
        'is_deleted': False,
    }


def test_update_flow__include_action_success(
    client, authorization, flow, environment, read_from_db, landing_pages_base_path
):
    request_payload = {
        'orderValue': 4,
        'actionType': 'include',
        'isEnabled': True,
        'landingArchive': (_zip_bytes(), 'landing.zip'),
    }

    response = client.patch(
        f'/api/v2/core/flows/{flow["id"]}',
        headers={'Authorization': authorization},
        data=request_payload,
        content_type='multipart/form-data',
    )

    assert response.status_code == 200, response.text

    updated = read_from_db('flow')
    expected_landing_path = str(pathlib.Path(landing_pages_base_path) / str(updated['id']))
    assert updated == {
        'id': flow['id'],
        'created_at': mock.ANY,
        'campaign_id': flow['campaign_id'],
        'order_value': request_payload['orderValue'],
        'action_type': request_payload['actionType'],
        'redirect_url': None,
        'landing_path': expected_landing_path,
        'is_enabled': request_payload['isEnabled'],
        'is_deleted': False,
    }
    assert (pathlib.Path(updated['landing_path']) / 'index.html').exists()


def test_update_flow__requires_redirect_url_for_redirect_action(client, authorization, flow):
    response = client.patch(
        f'/api/v2/core/flows/{flow["id"]}',
        headers={'Authorization': authorization},
        data={
            'actionType': 'redirect',
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 422, response.text
    assert response.json == {
        'code': 422,
        'errors': {'form': {'redirectUrl': ['redirectUrl is required for redirect action.']}},
        'status': 'Unprocessable Entity',
    }


def test_update_flow__requires_landing_archive_for_include_action(client, authorization, flow):
    response = client.patch(
        f'/api/v2/core/flows/{flow["id"]}',
        headers={'Authorization': authorization},
        data={
            'actionType': 'include',
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 422, response.text
    assert response.json == {
        'code': 422,
        'errors': {'form': {'landingArchive': ['landingArchive is required for include action.']}},
        'status': 'Unprocessable Entity',
    }


def test_update_flow__rejects_non_zip_landing_archive(client, authorization, flow):
    response = client.patch(
        f'/api/v2/core/flows/{flow["id"]}',
        headers={'Authorization': authorization},
        data={
            'actionType': 'include',
            'landingArchive': (io.BytesIO(b'not-a-zip'), 'landing.txt'),
        },
        content_type='multipart/form-data',
    )

    assert response.status_code == 422, response.text
    assert response.json == {
        'code': 422,
        'errors': {'form': {'landingArchive': ['landingArchive must be a .zip file.']}},
        'status': 'Unprocessable Entity',
    }
