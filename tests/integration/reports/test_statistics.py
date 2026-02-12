from datetime import datetime, timedelta
from decimal import Decimal


def test_get_report(client, authorization, campaign, statistics_expenses, timestamp):
    start_timestamp = timestamp - 5 * 24 * 60 * 60
    end_timestamp = timestamp

    response = client.get(
        '/api/v2/reports/statistics',
        headers={'Authorization': authorization},
        query_string={
            'campaignId': campaign['id'],
            'periodStart': start_timestamp,
            'periodEnd': end_timestamp,
        },
    )
    assert response.status_code == 200, response.text

    start_date = datetime.fromtimestamp(start_timestamp)
    end_date = datetime.fromtimestamp(end_timestamp)
    campaign_id = campaign['id']

    assert response.json == {
        'content': {
            'parameters': [
                'utm_source',
                'utm_content',
                'utm_campaign',
                'utm_medium',
                'ad_name',
                'utm_id',
                'redirect_url',
                'pixel',
                'utm_term',
                'adset_name',
                'fbclid',
            ],
            'report': [
                {'date': start_date.strftime('%Y-%m-%d'), 'clicks': 0, 'payouts': 0, 'expenses': None, 'roi': None},
                {
                    'date': (start_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'clicks': 0,
                    'payouts': 0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'clicks': 0,
                    'payouts': 0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'clicks': 2,
                    'leads': 2,
                    'lead_status': 'accept',
                    'payouts': 2 * float(campaign['cost_value']),
                    'expenses': sum(statistics_expenses[campaign_id][(start_date + timedelta(days=3)).date()].values()),
                    'roi': float(
                        Decimal(
                            (
                                2 * float(campaign['cost_value'])
                                - sum(
                                    statistics_expenses[campaign_id][(start_date + timedelta(days=3)).date()].values()
                                )
                            )
                            / sum(statistics_expenses[campaign_id][(start_date + timedelta(days=3)).date()].values())
                            * 100
                        ).quantize(Decimal('0.00'))
                    ),
                },
                {
                    'date': (start_date + timedelta(days=4)).strftime('%Y-%m-%d'),
                    'clicks': 2,
                    'leads': 2,
                    'lead_status': 'accept',
                    'payouts': 2 * float(campaign['cost_value']),
                    'expenses': sum(statistics_expenses[campaign_id][(start_date + timedelta(days=4)).date()].values()),
                    'roi': float(
                        Decimal(
                            (
                                2 * float(campaign['cost_value'])
                                - sum(
                                    statistics_expenses[campaign_id][(start_date + timedelta(days=4)).date()].values()
                                )
                            )
                            / sum(statistics_expenses[campaign_id][(start_date + timedelta(days=4)).date()].values())
                            * 100
                        ).quantize(Decimal('0.00'))
                    ),
                },
                {
                    'date': (start_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'accept',
                    'payouts': 1 * float(campaign['cost_value']),
                    'expenses': sum(statistics_expenses[campaign_id][(start_date + timedelta(days=5)).date()].values()),
                    'roi': float(
                        Decimal(
                            (
                                2 * float(campaign['cost_value'])
                                - sum(
                                    statistics_expenses[campaign_id][(start_date + timedelta(days=5)).date()].values()
                                )
                            )
                            / sum(statistics_expenses[campaign_id][(start_date + timedelta(days=5)).date()].values())
                            * 100
                        ).quantize(Decimal('0.00'))
                    ),
                },
                {
                    'date': end_date.strftime('%Y-%m-%d'),
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'reject',
                    'payouts': 0.0,
                    'expenses': None,
                    'roi': None,
                },
            ],
        }
    }


def test_get_report__group_by_parameter(client, authorization, statistics_expenses, campaign_id, timestamp):
    start_timestamp = timestamp - 4 * 24 * 60 * 60
    end_timestamp = timestamp

    response = client.get(
        '/api/v2/reports/statistics',
        headers={'Authorization': authorization},
        query_string={
            'campaignId': campaign_id,
            'periodStart': timestamp - 4 * 24 * 60 * 60,
            'periodEnd': timestamp,
            'groupParameters': 'ad_name,adset_name',
        },
    )

    assert response.status_code == 200, response.text

    start_date = datetime.fromtimestamp(start_timestamp)
    end_date = datetime.fromtimestamp(end_timestamp)

    assert response.json == {
        'content': {
            'parameters': [
                'utm_source',
                'utm_content',
                'utm_campaign',
                'utm_medium',
                'ad_name',
                'utm_id',
                'redirect_url',
                'pixel',
                'utm_term',
                'adset_name',
                'fbclid',
            ],
            'report': [
                {'date': start_date.strftime('%Y-%m-%d'), 'clicks': 0, 'payouts': 0, 'expenses': None, 'roi': None},
                {
                    'date': (start_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'clicks': 0,
                    'payouts': 0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'ad_name': 'ad_0',
                    'adset_name': 'adset9',
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'accept',
                    'payouts': 5.0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'ad_name': 'ad_1',
                    'adset_name': 'adset9',
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'accept',
                    'payouts': 5.0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'ad_name': 'ad_0',
                    'adset_name': 'adset9',
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'accept',
                    'payouts': 5.0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'ad_name': 'ad_1',
                    'adset_name': 'adset9',
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'accept',
                    'payouts': 5.0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': end_date.strftime('%Y-%m-%d'),
                    'ad_name': 'ad_1',
                    'adset_name': 'adset9',
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'accept',
                    'payouts': 5.0,
                    'expenses': None,
                    'roi': None,
                },
                {
                    'date': end_date.strftime('%Y-%m-%d'),
                    'ad_name': 'ad_0',
                    'adset_name': 'adset9',
                    'clicks': 1,
                    'leads': 1,
                    'lead_status': 'reject',
                    'payouts': 0.0,
                    'expenses': None,
                    'roi': None,
                },
            ],
        }
    }


def test_get_report__no_statistics(client, authorization, timestamp):
    start_timestamp = timestamp - 4 * 24 * 60 * 60
    end_timestamp = timestamp

    response = client.get(
        '/api/v2/reports/statistics',
        headers={'Authorization': authorization},
        query_string={
            'campaignId': 100500,
            'periodStart': start_timestamp,
            'periodEnd': end_timestamp,
        },
    )
    assert response.status_code == 200, response.text

    start_date = datetime.fromtimestamp(start_timestamp)
    end_date = datetime.fromtimestamp(end_timestamp)

    assert response.json == {
        'content': {
            'parameters': [],
            'report': [
                {'date': start_date.strftime('%Y-%m-%d'), 'clicks': 0},
                {'date': (start_date + timedelta(days=1)).strftime('%Y-%m-%d'), 'clicks': 0},
                {'date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'), 'clicks': 0},
                {'date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'), 'clicks': 0},
                {'date': end_date.strftime('%Y-%m-%d'), 'clicks': 0},
            ],
        }
    }
