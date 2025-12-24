from flask.views import MethodView

from src.blueprint import Blueprint
from src.container import container
from src.tracker.schemas import TrackClickRequestSchema, TrackPostbackRequest
from src.tracker.services import TrackService

blueprint = Blueprint('tracker', __name__, description='Tracker')


@blueprint.route('/click')
class TrackClick(MethodView):
    @blueprint.arguments(TrackClickRequestSchema)
    @blueprint.response(201)
    def post(self, track_payload):
        track_click_service = container.get(TrackService)

        track_click_service.track_click(
            track_payload.pop('click_id'), track_payload.pop('campaign_id'), parameters=track_payload
        )


@blueprint.route('/postback')
class TrackPostback(MethodView):
    @blueprint.arguments(TrackPostbackRequest, location='query')
    @blueprint.response(201)
    def get(self, track_payload):
        track_click_service = container.get(TrackService)

        track_click_service.track_postback(track_payload.pop('click_id'), parameters=track_payload)

    @blueprint.arguments(TrackPostbackRequest)
    @blueprint.response(201)
    def post(self, track_payload):
        track_click_service = container.get(TrackService)

        track_click_service.track_postback(track_payload.pop('click_id'), parameters=track_payload)
