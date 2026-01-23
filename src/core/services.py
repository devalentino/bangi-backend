import logging
import os
import shutil
import tempfile
import zipfile
from typing import Annotated

from wireup import service, Inject

from peewee import fn
from src.core.entities import Campaign, Flow
from src.core.enums import FlowActionType, SortOrder
from src.core.exceptions import LandingPageUploadError


logger = logging.getLogger(__name__)

@service
class CampaignService:
    def get(self, id):
        return Campaign.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(Campaign, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [c for c in Campaign.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def all(self):
        return [c for c in Campaign.select()]

    def create(self, name, cost_model, cost_value, currency, status_mapper=None):
        campaign = Campaign(
            name=name,
            cost_model=cost_model,
            cost_value=cost_value,
            currency=currency,
            status_mapper=status_mapper,
        )
        campaign.save()
        return campaign

    def update(self, campaign_id, name=None, cost_model=None, cost_value=None, currency=None, status_mapper=None):
        campaign = Campaign.get_by_id(campaign_id)

        if name:
            campaign.name = name

        if cost_model:
            campaign.cost_model = cost_model

        if cost_value:
            campaign.cost_value = cost_value

        if currency:
            campaign.currency = currency

        if status_mapper is not None:
            campaign.status_mapper = status_mapper

        campaign.save()

        return campaign

    def count(self):
        return Campaign.select(fn.count(Campaign.id)).scalar()


@service
class FlowService:
    def __init__(self, landing_pages_base_path: Annotated[str, Inject(param='LANDING_PAGES_BASE_PATH')]):
        self.landing_pages_base_path = landing_pages_base_path
    def _store_landing_archive(self, flow_id, landing_archive):
        if not self.landing_pages_base_path:
            logger.error('Landing archives base path is not configured')
            raise LandingPageUploadError()

        flow_dir = os.path.join(self.landing_pages_base_path, str(flow_id))
        if os.path.exists(flow_dir):
            shutil.rmtree(flow_dir)
        os.makedirs(flow_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            landing_archive.save(temp_file.name)
            temp_path = temp_file.name

        try:
            with zipfile.ZipFile(temp_path) as archive:
                archive.extractall(flow_dir)
        finally:
            os.remove(temp_path)

        return flow_dir

    def get(self, id):
        return Flow.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(Flow, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [
            f
            for f in Flow.select().where(Flow.is_deleted == False).order_by(order_by).limit(page_size).offset(page - 1)
        ]

    def create(
        self,
        campaign_id,
        order_value,
        action_type,
        redirect_url=None,
        is_enabled=True,
        landing_archive=None,
    ):
        flow = Flow(
            campaign_id=campaign_id,
            order_value=order_value,
            action_type=action_type,
            redirect_url=redirect_url,
            is_enabled=is_enabled,
        )
        flow.save()

        if action_type == FlowActionType.include:
            landing_path = self._store_landing_archive(flow, landing_archive)
            flow.landing_path = landing_path
            flow.save()

        return flow

    def update(
        self,
        flow_id,
        order_value=None,
        action_type=None,
        redirect_url=None,
        is_enabled=None,
        landing_archive=None,
    ):
        flow = Flow.get_by_id(flow_id)
        action_type_value = self._normalize_action_type(action_type)
        flow.order_value = order_value
        flow.action_type = action_type_value
        flow.redirect_url = redirect_url
        flow.is_enabled = is_enabled

        if action_type_value == FlowActionType.include:
            self._store_landing_archive(flow, landing_archive)
        elif action_type_value == FlowActionType.redirect:
            flow.landing_path = None

        flow.save()
        return flow

    def count(self):
        return Flow.select(fn.count(Flow.id)).where(Flow.is_deleted == False).scalar()
