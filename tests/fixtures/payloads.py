import pytest


@pytest.fixture
def campaign_name():
    return 'Test Campaign'


@pytest.fixture
def status_mapper():
    return {
        'parameter': 'state',
        'mapping': {'executed': 'approved', 'failed': 'rejected'},
    }


@pytest.fixture
def campaign_payload(campaign_name, status_mapper):
    return {
        'name': campaign_name,
        'cost_model': 'cpa',
        'cost_value': 10,
        'currency': 'usd',
        'status_mapper': status_mapper,
    }
