import json
from collections import defaultdict
from datetime import datetime, timedelta

from wireup import service

from src.core.utils import utcnow
from src.reports.repositories import BaseReportRepository


@service
class ReportService:
    def __init__(self, base_report_repository: BaseReportRepository):
        self.base_report_repository = base_report_repository

    def _build_base_report(self, report_rows, parameters):
        report = defaultdict(lambda: defaultdict(dict))
        for clicks_count, leads_count, lead_status, date, *parameters_values in report_rows:
            report[date]['clicks'] = report[date].get('clicks', 0) + clicks_count
            if lead_status:
                report[date]['leads'][lead_status] = leads_count

            for parameter_name, parameter_value in zip(parameters['group_parameters'], parameters_values):
                report[date]['parameters'][parameter_name] = parameter_value

        period_start_date = datetime.fromtimestamp(parameters['period_start']).date()
        period_end_date = utcnow().date()
        if parameters['period_end']:
            period_end_date = datetime.fromtimestamp(parameters['period_end']).date()

        all_dates_report = defaultdict(lambda: defaultdict(dict))
        days_delta = period_end_date - period_start_date
        for day in range(days_delta.days + 1):
            date = (period_start_date + timedelta(days=day)).strftime('%Y-%m-%d')
            payload = report[date] if date in report else {'clicks': 0}
            all_dates_report[date] = payload

        return all_dates_report

    def base_report(self, parameters):
        report_rows, available_parameters_row = self.base_report_repository.get(parameters)
        report = self._build_base_report(report_rows, parameters)

        available_parameters = []
        if available_parameters_row:
            (available_parameters_row,) = available_parameters_row
            available_parameters = list(json.loads(available_parameters_row).keys()) if available_parameters_row else []

        return report, available_parameters
