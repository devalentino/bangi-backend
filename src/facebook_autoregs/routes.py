import humps
from flask.views import MethodView
from playhouse.shortcuts import model_to_dict

from src.auth import auth
from src.blueprint import Blueprint
from src.container import container
from src.core.schemas import PaginationRequestSchema
from src.facebook_autoregs.schemas import (
    AdCabinetListResponseSchema,
    AdCabinetRequestSchema,
    AdCabinetResponseSchema,
    BusinessManagerListResponseSchema,
    BusinessManagerRequestSchema,
    BusinessManagerResponseSchema,
    ExecutorListResponseSchema,
    ExecutorRequestSchema,
    ExecutorResponseSchema,
)
from src.facebook_autoregs.services import AdCabinetService, BusinessManagerService, ExecutorService

blueprint = Blueprint('extension_facebook_autoregs', __name__, description='Facebook Autoregs Extension')


@blueprint.route('/executors')
class Executors(MethodView):
    @blueprint.arguments(PaginationRequestSchema, location='query')
    @blueprint.response(200, ExecutorListResponseSchema)
    @auth.login_required
    def get(self, parameters_payload):
        executor_service = container.get(ExecutorService)
        executors = executor_service.list(
            parameters_payload['page'],
            parameters_payload['page_size'],
            parameters_payload['sort_by'],
            parameters_payload['sort_order'],
        )
        count = executor_service.count()

        return {
            'content': [humps.camelize(model_to_dict(e)) for e in executors],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(ExecutorRequestSchema)
    @blueprint.response(201)
    @auth.login_required
    def post(self, executor_payload):
        executor_service = container.get(ExecutorService)
        executor_service.create(executor_payload['name'])


@blueprint.route('/executors/<int:executor_id>')
class Executor(MethodView):
    @blueprint.response(200, ExecutorResponseSchema)
    @auth.login_required
    def get(self, executor_id):
        executor_service = container.get(ExecutorService)
        executor = executor_service.get(executor_id)
        return humps.camelize(model_to_dict(executor))

    @blueprint.arguments(ExecutorRequestSchema)
    @blueprint.response(200)
    @auth.login_required
    def patch(self, executor_payload, executor_id):
        executor_service = container.get(ExecutorService)
        executor_service.update(executor_id, executor_payload.get('name'))


@blueprint.route('/business-managers')
class BusinessManagers(MethodView):
    @blueprint.arguments(PaginationRequestSchema, location='query')
    @blueprint.response(200, BusinessManagerListResponseSchema)
    @auth.login_required
    def get(self, parameters_payload):
        business_manager_service = container.get(BusinessManagerService)
        business_managers = business_manager_service.list(
            parameters_payload['page'],
            parameters_payload['page_size'],
            parameters_payload['sort_by'],
            parameters_payload['sort_order'],
        )
        count = business_manager_service.count()

        return {
            'content': [humps.camelize(model_to_dict(b)) for b in business_managers],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(BusinessManagerRequestSchema)
    @blueprint.response(201)
    @auth.login_required
    def post(self, business_manager_payload):
        business_manager_service = container.get(BusinessManagerService)
        business_manager_service.create(business_manager_payload['name'])


@blueprint.route('/business-managers/<int:business_manager_id>')
class BusinessManager(MethodView):
    @blueprint.response(200, BusinessManagerResponseSchema)
    @auth.login_required
    def get(self, business_manager_id):
        business_manager_service = container.get(BusinessManagerService)
        business_manager = business_manager_service.get(business_manager_id)
        return humps.camelize(model_to_dict(business_manager))

    @blueprint.arguments(BusinessManagerRequestSchema)
    @blueprint.response(200)
    @auth.login_required
    def patch(self, business_manager_payload, business_manager_id):
        business_manager_service = container.get(BusinessManagerService)
        business_manager_service.update(business_manager_id, business_manager_payload.get('name'))


@blueprint.route('/ad-cabinets')
class AdCabinets(MethodView):
    @blueprint.arguments(PaginationRequestSchema, location='query')
    @blueprint.response(200, AdCabinetListResponseSchema)
    @auth.login_required
    def get(self, parameters_payload):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinets = ad_cabinet_service.list(
            parameters_payload['page'],
            parameters_payload['page_size'],
            parameters_payload['sort_by'],
            parameters_payload['sort_order'],
        )
        count = ad_cabinet_service.count()

        return {
            'content': [humps.camelize(model_to_dict(ac)) for ac in ad_cabinets],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(AdCabinetRequestSchema)
    @blueprint.response(201)
    @auth.login_required
    def post(self, ad_cabinet_payload):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet_service.create(ad_cabinet_payload['name'])


@blueprint.route('/ad-cabinets/<int:ad_cabinet_id>')
class AdCabinet(MethodView):
    @blueprint.response(200, AdCabinetResponseSchema)
    @auth.login_required
    def get(self, ad_cabinet_id):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet = ad_cabinet_service.get(ad_cabinet_id)
        return humps.camelize(model_to_dict(ad_cabinet))

    @blueprint.arguments(AdCabinetRequestSchema)
    @blueprint.response(200)
    @auth.login_required
    def patch(self, ad_cabinet_payload, ad_cabinet_id):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet_service.update(ad_cabinet_id, ad_cabinet_payload.get('name'))
