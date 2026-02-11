import json
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest


@pytest.fixture
def campaign_cost_value():
    return 5.0


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
def statistics_clicks(write_to_db, click_parameters, postback_parameters, campaign_cost_value, timestamp):
    clicks = defaultdict(list)

    for campaign_index in range(2):
        campaign = write_to_db(
            'campaign',
            {
                'name': f'Campaign {campaign_index}',
                'expenses_distribution_parameter': 'ad_name',
                'cost_model': 'cpa',
                'cost_value': campaign_cost_value,
            },
        )

        for day in range(3):
            for ad_index in range(2):
                created_at = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=day)).timestamp()

                click = write_to_db(
                    'track_click',
                    {
                        'click_id': uuid4(),
                        'campaign_id': campaign['id'],
                        'parameters': click_parameters
                        | {'redirect_url': f'http://localhost/?ci={campaign_index}', 'ad_name': f'ad_{ad_index}'},
                        'created_at': created_at,
                    },
                )
                clicks[campaign['id']].append(click)

                for status in 'expect', 'accept':
                    write_to_db(
                        'track_postback',
                        {
                            'click_id': click['click_id'],
                            'parameters': postback_parameters | {'status': status},
                            'cost_value': campaign_cost_value,
                            'created_at': created_at,
                        },
                    )

    # first campaign and first click, second campaign and last click got rejected
    for click in clicks[1][0], clicks[2][-1]:
        write_to_db(
            'track_postback',
            {
                'click_id': click['click_id'],
                'parameters': postback_parameters | {'status': 'reject'},
                'created_at': timestamp,
            },
        )

    return clicks


@pytest.fixture
def statistics_expenses(statistics_clicks, timestamp, write_to_db):
    statistics_expenses = defaultdict(dict)

    for campaign_id, clicks in statistics_clicks.items():
        date2distribution = defaultdict(dict)
        for click in clicks:
            date = datetime.fromtimestamp(click['created_at']).date()
            click_parameters = json.loads(click['parameters'])
            ad_name = click_parameters['ad_name']

            date2distribution[date][ad_name] = round(random.uniform(0, 100), 2)

        for date, distribution in date2distribution.items():
            write_to_db(
                'expense',
                {'campaign_id': campaign_id, 'date': date, 'distribution': distribution, 'created_at': timestamp},
            )

        statistics_expenses[campaign_id] = date2distribution

    return statistics_expenses
