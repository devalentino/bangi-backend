import humps
from flask.views import MethodView
from playhouse.shortcuts import model_to_dict

from src.auth import auth
from src.blueprint import Blueprint
from src.container import container
from src.core.schemas import PaginationRequestSchema
from src.facebook_autoregs.schemas import ExecutorListResponseSchema, ExecutorRequestSchema, ExecutorResponseSchema
from src.facebook_autoregs.services import ExecutorService

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


#
#
# @blueprint.route('/filters/campaigns')
# class FilterCampaigns(MethodView):
#     @blueprint.response(200, FilterCampaignResponseSchema(many=True))
#     @auth.login_required
#     def get(self):
#         campaign_service = container.get(CampaignService)
#         campaigns = campaign_service.all()
#         return [model_to_dict(c) for c in campaigns]
