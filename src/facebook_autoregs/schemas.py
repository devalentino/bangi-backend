from marshmallow import fields

from src.core.schemas import PaginationResponseSchema, Schema


class ExecutorRequestSchema(Schema):
    name = fields.String(required=True)


class ExecutorResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)


class ExecutorListResponseSchema(Schema):
    content = fields.Nested(ExecutorResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)


class BusinessManagerRequestSchema(Schema):
    name = fields.String(required=True)


class BusinessManagerResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)


class BusinessManagerListResponseSchema(Schema):
    content = fields.Nested(BusinessManagerResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)


class AdCabinetRequestSchema(Schema):
    name = fields.String(required=True)


class AdCabinetResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)


class AdCabinetListResponseSchema(Schema):
    content = fields.Nested(AdCabinetResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)
