import json
from unittest import mock

import pytest


class TestExpensesReport:
    @pytest.fixture
    def expenses_distribution_parameter(self):
        return 'ad_name'

    def test_post_expenses_report(self, client, authorization, campaign, today, read_from_db):
        request_payload = {
            'campaignId': campaign['id'],
            'distributionParameter': 'ad_name',
            'dates': [
                {'date': today.isoformat(), 'distribution': {'ad1': 12.5, 'ad2': 7.5}},
            ],
        }

        assert request_payload['distributionParameter'] == campaign['expenses_distribution_parameter']

        response = client.post(
            '/api/v2/reports/expenses',
            headers={'Authorization': authorization},
            json=request_payload,
        )

        assert response.status_code == 200, response.text

        expense = read_from_db('expense')
        assert expense == {
            'id': mock.ANY,
            'created_at': mock.ANY,
            'campaign_id': campaign['id'],
            'date': today,
            'distribution': mock.ANY,
        }

        assert json.loads(expense['distribution']) == request_payload['dates'][0]['distribution']

    def test_post_expenses_report__expense_exists(
        self, client, authorization, campaign, today, read_from_db, write_to_db
    ):
        existing_expense = write_to_db(
            'expense',
            {'campaign_id': campaign['id'], 'date': today, 'distribution': json.dumps({'ad1': 1.5, 'ad2': 0.5})},
        )

        request_payload = {
            'campaignId': campaign['id'],
            'distributionParameter': 'ad_name',
            'dates': [
                {'date': today.isoformat(), 'distribution': {'ad1': 12.5, 'ad2': 7.5}},
            ],
        }

        assert existing_expense['distribution'] != request_payload['dates'][0]['distribution']

        response = client.post(
            '/api/v2/reports/expenses',
            headers={'Authorization': authorization},
            json=request_payload,
        )

        assert response.status_code == 200, response.text

        expense = read_from_db('expense')

        assert json.loads(expense['distribution']) != json.loads(existing_expense['distribution'])
        assert json.loads(expense['distribution']) == request_payload['dates'][0]['distribution']


class TestExpensesReportExpensesDistributionParameterNotSet:
    def test_post_expenses_report(self, client, authorization, campaign, today, read_from_db):
        assert campaign['expenses_distribution_parameter'] is None

        request_payload = {
            'campaignId': campaign['id'],
            'distributionParameter': 'ad_name',
            'dates': [
                {'date': today.isoformat(), 'distribution': {'ad1': 12.5, 'ad2': 7.5}},
            ],
        }

        response = client.post(
            '/api/v2/reports/expenses',
            headers={'Authorization': authorization},
            json=request_payload,
        )

        assert response.status_code == 200, response.text

        expense = read_from_db('expense')
        assert expense == {
            'id': mock.ANY,
            'created_at': mock.ANY,
            'campaign_id': campaign['id'],
            'date': today,
            'distribution': mock.ANY,
        }

        assert json.loads(expense['distribution']) == request_payload['dates'][0]['distribution']


class TestDistributionParameterIsChanged:
    @pytest.fixture
    def expenses_distribution_parameter(self):
        return 'adset_name'

    def test_post_expenses_report(self, client, authorization, campaign, today):
        request_payload = {
            'campaignId': campaign['id'],
            'distributionParameter': 'ad_name',
            'dates': [
                {'date': today.isoformat(), 'distribution': {'ad1': 12.5, 'ad2': 7.5}},
            ],
        }

        assert request_payload['distributionParameter'] != campaign['expenses_distribution_parameter']

        response = client.post(
            '/api/v2/reports/expenses',
            headers={'Authorization': authorization},
            json=request_payload,
        )

        assert response.status_code == 400, response.text
        assert response.json == {'message': 'Bad distribution parameter'}
