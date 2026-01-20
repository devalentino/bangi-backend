import logging
from typing import Optional

from wireup import service

from src.core.entities import Campaign
from src.tracker.entities import TrackClick, TrackPostback
from src.tracker.enums import Status

logger = logging.getLogger(__name__)


@service
class TrackService:
    def track_click(self, click_id: str, campaign_id: str, parameters: dict) -> None:
        click = TrackClick(click_id=click_id, campaign_id=campaign_id, parameters=parameters)
        click.save()

    def track_postback(self, click_id: str, parameters: dict) -> None:
        status = self._map_status(click_id, parameters)
        postback = TrackPostback(click_id=click_id, parameters=parameters, status=status)
        postback.save()

    def _map_status(self, click_id: str, parameters: dict) -> Optional[str]:
        click = TrackClick.get_or_none(TrackClick.click_id == click_id)
        if click is None:
            logger.warning('Failed to find click', extra={'click_id': click_id})
            return None

        campaign = Campaign.get_or_none(Campaign.id == click.campaign_id)
        if campaign is None or not campaign.status_mapper:
            logger.warning('Failed to find campaign', extra={'campaign_id': click.campaign_id})
            return None

        if not isinstance(campaign.status_mapper, dict):
            logger.warning('Failed to get status mapper', extra={'campaign_id': click.campaign_id})
            return None

        status_param = campaign.status_mapper.get('parameter')
        if not status_param:
            logger.warning('Failed to get status parameter', extra={'status_mapper': campaign.status_mapper})
            return None

        external_status = parameters.get(status_param)
        if external_status is None:
            logger.warning(
                'Failed to get external status', extra={'status_param': status_param, 'parameters': parameters}
            )
            return None

        status_mapping = campaign.status_mapper.get('mapping') or {}
        internal_status = status_mapping.get(external_status)

        if internal_status in {s.value for s in Status}:
            return internal_status

        logger.warning(
            'Failed to mapped status', extra={'status_mapping': status_mapping, 'external_status': external_status}
        )
        return None
