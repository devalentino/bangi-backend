from datetime import datetime, timedelta, timezone

import pytest


@pytest.fixture
def executor_name():
    return 'Khalid ibn al-Walid'


@pytest.fixture
def ad_cabinet_name():
    return 'Muhammad ibn Musa al-Khwarizmi'


@pytest.fixture
def business_portfolio_name():
    return 'Abd Allah ibn Abi Quhafa'


@pytest.fixture
def business_page_name():
    return 'Al-Tabari'


@pytest.fixture
def executor_payload(executor_name):
    return {
        'name': executor_name,
        'is_banned': False,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def ad_cabinet_payload(ad_cabinet_name):
    return {
        'name': ad_cabinet_name,
        'is_banned': False,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def business_portfolio_payload(business_portfolio_name):
    return {
        'name': business_portfolio_name,
        'is_banned': False,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def business_page_payload(business_page_name):
    return {
        'name': business_page_name,
        'is_banned': False,
        'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)).timestamp(),
    }


@pytest.fixture
def executor(write_to_db, executor_payload):
    return write_to_db('facebook_autoregs_executor', executor_payload)


@pytest.fixture
def ad_cabinet(write_to_db, ad_cabinet_payload):
    return write_to_db('facebook_autoregs_ad_cabinet', ad_cabinet_payload)


@pytest.fixture
def business_portfolio(write_to_db, business_portfolio_payload):
    return write_to_db('facebook_autoregs_business_portfolio', business_portfolio_payload)


@pytest.fixture
def business_page(write_to_db, business_page_payload):
    return write_to_db('facebook_autoregs_business_page', business_page_payload)
