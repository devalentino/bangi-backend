from marshmallow import INCLUDE, fields

from src.core.schemas import ComaSeparatedStringsField, Schema


class BaseReportRequest(Schema):
    campaign_id = fields.Integer(required=True)
    period_start = fields.Integer(required=True)
    period_end = fields.Integer(required=False)
    group_parameters = ComaSeparatedStringsField(dump_default=[], load_default=[])

    class Meta:
        unknown = INCLUDE


class BaseReportContent(Schema):
    report = fields.Dict()
    parameters = fields.List(fields.String)


class BaseReportResponse(Schema):
    content = fields.Nested(BaseReportContent())
