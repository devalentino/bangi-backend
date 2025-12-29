from marshmallow import fields

from src.core.schemas import PaginationResponseSchema, Schema


class BusinessManagerNestedResponseSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    isBanned = fields.Boolean(required=True)


class ExecutorRequestSchema(Schema):
    name = fields.String(required=True)
    isBanned = fields.Boolean(required=True)


class ExecutorResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)


class ExecutorListResponseSchema(Schema):
    content = fields.Nested(ExecutorResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)


class AdCabinetRequestSchema(Schema):
    name = fields.String(required=True)
    isBanned = fields.Boolean(required=True)


class AdCabinetResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)
    businessManager = fields.Nested(BusinessManagerNestedResponseSchema())


class AdCabinetListResponseSchema(Schema):
    content = fields.Nested(AdCabinetResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)


class BusinessManagerRequestSchema(Schema):
    name = fields.String(required=True)
    isBanned = fields.Boolean(required=True)


class BusinessManagerResponseSchema(ExecutorRequestSchema):
    id = fields.Integer(required=True)
    executors = fields.Nested(ExecutorResponseSchema(many=True), required=True)
    adCabinets = fields.Nested(AdCabinetResponseSchema(many=True), required=True)


class BusinessManagerListResponseSchema(Schema):
    content = fields.Nested(BusinessManagerResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)


class CampaignRequestSchema(Schema):
    name = fields.String(required=True)
    executorId = fields.Integer(required=True)
    adCabinetId = fields.Integer(required=True)


class CampaignResponseSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    executor = fields.Nested(ExecutorResponseSchema, required=True)
    adCabinet = fields.Nested(AdCabinetResponseSchema, required=True)


class CampaignListResponseSchema(Schema):
    content = fields.Nested(CampaignResponseSchema(many=True), required=True)
    pagination = fields.Nested(PaginationResponseSchema, required=True)
