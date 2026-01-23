import io
import zipfile

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
            'include_path': None,
            'is_enabled': True,
            'is_deleted': False,
        },
    )


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
