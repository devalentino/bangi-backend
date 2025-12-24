from collections import defaultdict
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest


@pytest.fixture
def click_parameters():
    return {
        'utm_source': 'fb',
        'utm_content': '000000000000000000',
        'utm_campaign': 'offer-1',
        'utm_medium': 'paid',
        'ad_name': 'ad1_1',
        'utm_id': '000000000000000000',
        'redirect_url': 'http://localhost/',
        'pixel': '0000000000000000',
        'utm_term': '000000000000000000',
        'adset_name': 'adset9',
        'fbclid': '0-0-0-0',
    }


@pytest.fixture
def postback_parameters():
    return {
        'sale_status': 'confirm',
        'lead_status': 'accept,expect',
        'check_sum': '0000000000000000000000000000000000000000',
        'payout': '0',
        'status': 'accept',
        'from': 'Terraleads.com',
        'return': 'OK',
        'offer_id': '0000',
        'rejected_status': 'reject,fail,trash,error',
        'tid': '00000000',
    }


@pytest.fixture
def statistics(write_to_db, click_parameters, postback_parameters):
    clicks = defaultdict(list)

    for ci in range(2):
        campaign = write_to_db('campaign', {'name': f'Campaign {ci}'})
        for tci in range(2):
            for day in range(3):
                click = write_to_db(
                    'track_click',
                    {
                        'click_id': uuid4(),
                        'campaign_id': campaign['id'],
                        'parameters': click_parameters
                        | {'redirect_url': f'http://localhost/?ci={ci}', 'ad_name': f'ad{ci}_{tci}'},
                        'created_at': (
                            datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=day)
                        ).timestamp(),
                    },
                )
                clicks[campaign['id']].append(click)

                for status in 'accept', 'expect':
                    write_to_db(
                        'track_postback',
                        {
                            'click_id': click['click_id'],
                            'parameters': postback_parameters | {'status': status},
                            'created_at': (
                                datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=day)
                            ).timestamp(),
                        },
                    )

    # first campaign and first click, second campaign and last click got rejected
    for click in clicks[1][0], clicks[2][-1]:
        write_to_db(
            'track_postback',
            {
                'click_id': click['click_id'],
                'parameters': postback_parameters | {'status': 'reject'},
                'created_at': (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=day)).timestamp(),
            },
        )

    return clicks
