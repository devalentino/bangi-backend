import humps
from flask.views import MethodView

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
    CampaignListResponseSchema,
    CampaignRequestSchema,
    CampaignResponseSchema,
    ExecutorListResponseSchema,
    ExecutorRequestSchema,
    ExecutorResponseSchema,
)
from src.facebook_autoregs.services import AdCabinetService, BusinessManagerService, CampaignService, ExecutorService

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
            'content': [humps.camelize(e.to_dict()) for e in executors],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(ExecutorRequestSchema)
    @blueprint.response(201, ExecutorResponseSchema)
    @auth.login_required
    def post(self, executor_payload):
        executor_service = container.get(ExecutorService)
        executor = executor_service.create(executor_payload['name'], executor_payload['isBanned'])
        return humps.camelize(executor.to_dict())


@blueprint.route('/executors/<int:executor_id>')
class Executor(MethodView):
    @blueprint.response(200, ExecutorResponseSchema)
    @auth.login_required
    def get(self, executor_id):
        executor_service = container.get(ExecutorService)
        executor = executor_service.get(executor_id)
        return humps.camelize(executor.to_dict())

    @blueprint.arguments(ExecutorRequestSchema)
    @blueprint.response(200, ExecutorResponseSchema)
    @auth.login_required
    def patch(self, executor_payload, executor_id):
        executor_service = container.get(ExecutorService)
        executor = executor_service.update(executor_id, executor_payload.get('name'), executor_payload.get('isBanned'))
        return humps.camelize(executor.to_dict())


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
            'content': [humps.camelize(b.to_dict()) for b in business_managers],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(BusinessManagerRequestSchema)
    @blueprint.response(201, BusinessManagerResponseSchema)
    @auth.login_required
    def post(self, business_manager_payload):
        business_manager_service = container.get(BusinessManagerService)
        business_manager = business_manager_service.create(
            business_manager_payload['name'], business_manager_payload['isBanned']
        )
        return humps.camelize(business_manager.to_dict())


@blueprint.route('/business-managers/<int:business_manager_id>')
class BusinessManager(MethodView):
    @blueprint.response(200, BusinessManagerResponseSchema)
    @auth.login_required
    def get(self, business_manager_id):
        business_manager_service = container.get(BusinessManagerService)
        business_manager = business_manager_service.get(business_manager_id)
        return humps.camelize(business_manager.to_dict())

    @blueprint.arguments(BusinessManagerRequestSchema)
    @blueprint.response(200, BusinessManagerResponseSchema)
    @auth.login_required
    def patch(self, business_manager_payload, business_manager_id):
        business_manager_service = container.get(BusinessManagerService)
        business_manager = business_manager_service.update(
            business_manager_id, business_manager_payload.get('name'), business_manager_payload.get('isBanned')
        )
        return humps.camelize(business_manager.to_dict())


@blueprint.route('/business-managers/<int:business_manager_id>/executors/<int:executor_id>')
class BusinessManagerAssignExecutor(MethodView):
    @blueprint.response(201, BusinessManagerResponseSchema)
    @auth.login_required
    def post(self, business_manager_id, executor_id):
        business_manager_service = container.get(BusinessManagerService)
        business_manager = business_manager_service.bind_executor(business_manager_id, executor_id)
        return humps.camelize(business_manager.to_dict())

    @blueprint.response(204, BusinessManagerResponseSchema)
    @auth.login_required
    def delete(self, business_manager_id, executor_id):
        business_manager_service = container.get(BusinessManagerService)
        business_manager_service.unbind_executor(business_manager_id, executor_id)


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
            'content': [humps.camelize(ac.to_dict()) for ac in ad_cabinets],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(AdCabinetRequestSchema)
    @blueprint.response(201, AdCabinetResponseSchema)
    @auth.login_required
    def post(self, ad_cabinet_payload):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet = ad_cabinet_service.create(ad_cabinet_payload['name'], ad_cabinet_payload['isBanned'])
        return humps.camelize(ad_cabinet.to_dict())


@blueprint.route('/ad-cabinets/<int:ad_cabinet_id>')
class AdCabinet(MethodView):
    @blueprint.response(200, AdCabinetResponseSchema)
    @auth.login_required
    def get(self, ad_cabinet_id):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet = ad_cabinet_service.get(ad_cabinet_id)
        return humps.camelize(ad_cabinet.to_dict())

    @blueprint.arguments(AdCabinetRequestSchema)
    @blueprint.response(200, AdCabinetResponseSchema)
    @auth.login_required
    def patch(self, ad_cabinet_payload, ad_cabinet_id):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet = ad_cabinet_service.update(
            ad_cabinet_id, ad_cabinet_payload.get('name'), ad_cabinet_payload['isBanned']
        )
        return humps.camelize(ad_cabinet.to_dict())


@blueprint.route('/ad-cabinets/<int:ad_cabinet_id>/business-manager/<int:business_manager_id>')
class AdCabinetAssignBusinessManager(MethodView):
    @blueprint.response(201, AdCabinetResponseSchema)
    @auth.login_required
    def post(self, ad_cabinet_id, business_manager_id):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet = ad_cabinet_service.bind_business_manager(ad_cabinet_id, business_manager_id)
        return humps.camelize(ad_cabinet.to_dict())

    @blueprint.response(204)
    @auth.login_required
    def delete(self, ad_cabinet_id, business_manager_id):
        ad_cabinet_service = container.get(AdCabinetService)
        ad_cabinet_service.unbind_business_manager(ad_cabinet_id, business_manager_id)


@blueprint.route('/campaigns')
class Campaigns(MethodView):
    @blueprint.arguments(PaginationRequestSchema, location='query')
    @blueprint.response(200, CampaignListResponseSchema)
    @auth.login_required
    def get(self, parameters_payload):
        campaign_service = container.get(CampaignService)
        campaigns = campaign_service.list(
            parameters_payload['page'],
            parameters_payload['page_size'],
            parameters_payload['sort_by'],
            parameters_payload['sort_order'],
        )
        count = campaign_service.count()

        return {
            'content': [humps.camelize(c.to_dict()) for c in campaigns],
            'pagination': parameters_payload | {'total': count},
        }

    @blueprint.arguments(CampaignRequestSchema)
    @blueprint.response(201)
    @auth.login_required
    def post(self, campaign_payload):
        campaign_service = container.get(CampaignService)
        campaign_service.create(campaign_payload['name'])


@blueprint.route('/campaigns/<int:campaign_id>')
class Campaign(MethodView):
    @blueprint.response(200, CampaignResponseSchema)
    @auth.login_required
    def get(self, campaign_id):
        campaign_service = container.get(CampaignService)
        campaign = campaign_service.get(campaign_id)
        return humps.camelize(campaign.to_dict())

    @blueprint.arguments(CampaignRequestSchema)
    @blueprint.response(200)
    @auth.login_required
    def patch(self, campaign_payload, campaign_id):
        campaign_service = container.get(CampaignService)
        campaign_service.update(
            campaign_id,
            name=campaign_payload.get('name'),
            cost_value=campaign_payload.get('costValue'),
            currency=campaign_payload.get('currency'),
            ad_cabinet_id=campaign_payload.get('adCabinetId'),
            executor_id=campaign_payload.get('executorId'),
        )
