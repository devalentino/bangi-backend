import json
from datetime import datetime, time, timedelta

from wireup import service

from src.core.entities import Campaign
from src.core.enums import SortOrder
from src.core.services import CampaignService
from src.core.utils import utcnow
from src.reports.entities import Expense
from src.reports.exceptions import ExpensesDistributionParameterError
from src.reports.repositories import StatisticsReportRepository
from src.tracker.entities import TrackClick
from src.tracker.services import TrackService


@service
class ReportService:
    def __init__(
        self,
        campaign_service: CampaignService,
        track_service: TrackService,
        statistics_report_repository: StatisticsReportRepository,
    ):
        self.campaign_service = campaign_service
        self.track_service = track_service
        self.statistics_report_repository = statistics_report_repository

    def _build_statistics_report(self, report_rows, expenses_rows, expenses_distribution_parameter, parameters):
        date2distribution = {date: json.loads(distribution) for date, distribution in expenses_rows}

        report = []
        for clicks_count, leads_count, payouts, lead_status, date, *parameters_values in report_rows:
            report.append(
                {
                    'date': date,
                    'clicks': clicks_count,
                    'leads': leads_count,
                    'lead_status': lead_status,
                    'payouts': payouts,
                    **dict(zip(parameters['group_parameters'], parameters_values)),
                }
            )

        period_start_date = datetime.fromtimestamp(parameters['period_start']).date()
        period_end_date = utcnow().date()
        if parameters['period_end']:
            period_end_date = datetime.fromtimestamp(parameters['period_end']).date()

        all_dates_report = []
        days_delta = period_end_date - period_start_date
        for day in range(days_delta.days + 1):
            date = (period_start_date + timedelta(days=day)).strftime('%Y-%m-%d')
            records = [r for r in report if r['date'] == date] or [{'date': date, 'clicks': 0, 'payouts': 0}]

            # extend records with expenses
            if len(parameters['group_parameters']) == 0 and len(records) == 1:
                records[0]['expenses'] = sum(date2distribution[date].values)
            elif len(parameters['group_parameters']) == 1 and parameters['group_parameters'][0] == expenses_distribution_parameter:
                for record in records:
                    record['expenses'] = date2distribution[date][expenses_distribution_parameter]
            else:
                for record in records:
                    record['expenses'] = None

            all_dates_report.extend(records)

        # add roi
        for record in all_dates_report:
            record['roi'] = None
            if record['expenses']:
                record['roi'] = (record['payouts'] - record['expenses']) / record['expenses'] * 100

        return all_dates_report

    def statistics_report(self, parameters):
        campaign = self.campaign_service.get(parameters['campaign_id'])
        report_rows, expenses_rows, available_parameters_row = self.statistics_report_repository.get(parameters)
        report = self._build_statistics_report(report_rows, expenses_rows, campaign.expenses_distribution_parameter, parameters)

        available_parameters = []
        if available_parameters_row:
            (available_parameters_row,) = available_parameters_row
            available_parameters = list(json.loads(available_parameters_row).keys()) if available_parameters_row else []

        return report, available_parameters

    def submit_expenses(self, campaign_id, expenses_distribution_parameter, date_distributions):
        campaign = self.campaign_service.get(campaign_id)
        if campaign.expenses_distribution_parameter is None:
            campaign.expenses_distribution_parameter = expenses_distribution_parameter
            campaign.save()

        if campaign.expenses_distribution_parameter != expenses_distribution_parameter:
            raise ExpensesDistributionParameterError()

        for date_distribution in date_distributions:
            Expense.insert(
                campaign=campaign,
                date=date_distribution['date'],
                distribution=date_distribution['distribution'],
            ).on_conflict(
                update={Expense.distribution: date_distribution['distribution']},
            ).execute()

    def list_expenses(self, page, page_size, sort_by, sort_order, campaign_id, period_start=None, period_end=None):
        order_by = getattr(Expense, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        query = Expense.select(Expense, Campaign).join(Campaign).where(Expense.campaign == campaign_id)

        if period_start is not None:
            query = query.where(Expense.date >= period_start)

        if period_end is not None:
            query = query.where(Expense.date <= period_end)

        total = query.count()

        query = query.order_by(order_by).limit(page_size).offset((page - 1) * page_size)
        expenses = [e for e in query]
        if expenses:
            return expenses, total

        # cover case for no reports
        campaign = self.campaign_service.get(campaign_id)

        dates = self.track_service.get_click_dates(
            campaign.id,
            datetime.combine(period_start, time.min).timestamp(),
            datetime.combine(period_end, time.max).timestamp(),
        )
        if len(dates) == 0:
            dates = [datetime.today()]

        expenses = [Expense(campaign=campaign, date=d, distribution={}) for d in dates]

        return expenses, 0


@service
class ReportHelperService:
    def list_expenses_distribution_parameters(self, campaign_id):
        parameters = set()
        query = TrackClick.select(TrackClick.parameters).where(TrackClick.campaign_id == campaign_id)
        for click in query:
            if click.parameters:
                parameters.update(click.parameters.keys())

        return sorted(parameters)

    def list_expenses_distribution_parameter_values(self, campaign_id, parameter):
        values = set()
        query = TrackClick.select(TrackClick.parameters).where(TrackClick.campaign_id == campaign_id)
        for click in query:
            if not click.parameters or parameter not in click.parameters:
                continue
            value = click.parameters.get(parameter)
            values.add(value)

        return sorted(values)
