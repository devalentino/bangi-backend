from datetime import datetime, timedelta


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

    start_date = datetime.fromtimestamp(start_timestamp).date()
    end_date = datetime.fromtimestamp(end_timestamp).date()

    assert response.json == {
        'content': {
            'report': {
                start_date.isoformat(): {
                    'clicks': 0,
                    'statuses': {},
                    'expenses': 0,
                    'roi_accepted': 0,
                    'roi_expected': 0,
                },
                (start_date + timedelta(days=1)).isoformat(): {
                    'clicks': 0,
                    'statuses': {},
                    'expenses': 0,
                    'roi_accepted': 0,
                    'roi_expected': 0,
                },
                (start_date + timedelta(days=2)).isoformat(): {
                    'clicks': 0,
                    'statuses': {},
                    'expenses': 0,
                    'roi_accepted': 0,
                    'roi_expected': 0,
                },
                (start_date + timedelta(days=3)).isoformat(): {
                    'statuses': {
                        'accept': {'leads': 1, 'payouts': 1 * float(campaign['cost_value'])},
                        'trash': {'leads': 1, 'payouts': 0.0},
                    },
                    'clicks': 30,
                    'expenses': sum(statistics_expenses[start_date + timedelta(days=3)].values()),
                    'roi_accepted': (
                        1 * float(campaign['cost_value'])
                        - sum(statistics_expenses[start_date + timedelta(days=3)].values())
                    )
                    / sum(statistics_expenses[start_date + timedelta(days=3)].values())
                    * 100,
                    'roi_expected': (
                        1 * float(campaign['cost_value'])
                        - sum(statistics_expenses[start_date + timedelta(days=3)].values())
                    )
                    / sum(statistics_expenses[start_date + timedelta(days=3)].values())
                    * 100,
                },
                (start_date + timedelta(days=4)).isoformat(): {
                    'statuses': {
                        'accept': {'leads': 1, 'payouts': 1 * float(campaign['cost_value'])},
                        'expect': {'leads': 1, 'payouts': 1 * float(campaign['cost_value'])},
                        'reject': {'leads': 1, 'payouts': 0.0},
                    },
                    'clicks': 25,
                    'expenses': sum(statistics_expenses[start_date + timedelta(days=4)].values()),
                    'roi_accepted': (
                        1 * float(campaign['cost_value'])
                        - sum(statistics_expenses[start_date + timedelta(days=4)].values())
                    )
                    / sum(statistics_expenses[start_date + timedelta(days=4)].values())
                    * 100,
                    'roi_expected': (
                        1 * float(campaign['cost_value'])
                        + 1 * float(campaign['cost_value'])
                        - sum(statistics_expenses[start_date + timedelta(days=4)].values())
                    )
                    / sum(statistics_expenses[start_date + timedelta(days=4)].values())
                    * 100,
                },
                end_date.isoformat(): {
                    'statuses': {'accept': {'leads': 1, 'payouts': 1 * float(campaign['cost_value'])}},
                    'clicks': 8,
                    'expenses': sum(statistics_expenses[end_date].values()),
                    'roi_accepted': (1 * float(campaign['cost_value']) - sum(statistics_expenses[end_date].values()))
                    / sum(statistics_expenses[end_date].values())
                    * 100,
                    'roi_expected': (1 * float(campaign['cost_value']) - sum(statistics_expenses[end_date].values()))
                    / sum(statistics_expenses[end_date].values())
                    * 100,
                },
            },
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
        }
    }


def test_get_report__group_by_parameter(client, authorization, statistics_expenses, campaign, timestamp):
    start_timestamp = timestamp - 4 * 24 * 60 * 60
    end_timestamp = timestamp

    response = client.get(
        '/api/v2/reports/statistics',
        headers={'Authorization': authorization},
        query_string={
            'campaignId': campaign['id'],
            'periodStart': timestamp - 4 * 24 * 60 * 60,
            'periodEnd': timestamp,
            'groupParameters': 'utm_source,ad_name',
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
    assert response.status_code == 404, response.text
    assert response.json == {'message': 'Campaign does not exist'}
