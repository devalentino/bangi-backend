from marshmallow import fields

from src.core.schemas import PaginationResponseSchema, Schema


class ExecutorRequestSchema(Schema):
    name = fields.String(required=True)


class ExecutorResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)


class ExecutorListResponseSchema(Schema):
    content = fields.Nested(ExecutorResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)
