from wireup import service

from peewee import fn
from src.core.enums import CostModel, SortOrder
from src.core.services import CampaignService as CoreCampaignService
from src.facebook_autoregs import exceptions
from src.facebook_autoregs.entities import AdCabinet, BusinessManager, Campaign, Executor


@service
class ExecutorService:
    def get(self, id):
        try:
            return Executor.get_by_id(id)
        except Executor.DoesNotExist:
            raise exceptions.ExecutorDoesNotExist()

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(Executor, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [e for e in Executor.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name, is_banned):
        executor = Executor(name=name, is_banned=is_banned)
        executor.save()
        return executor

    def update(self, executor_id, name=None, is_banned=None):
        executor = Executor.get_by_id(executor_id)

        if name:
            executor.name = name

        if is_banned is not None:
            executor.is_banned = is_banned

        executor.save()
        return executor

    def count(self):
        return Executor.select(fn.count(Executor.id)).scalar()


@service
class BusinessManagerService:
    def __init__(self, executor_service: ExecutorService):
        self.executor_service = executor_service

    def get(self, id):
        return BusinessManager.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(BusinessManager, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [bm for bm in BusinessManager.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name, is_banned):
        business_manager = BusinessManager(name=name, is_banned=is_banned)
        business_manager.save()
        return business_manager

    def update(self, business_manager_id, name=None, is_banned=None):
        business_manager = BusinessManager.get_by_id(business_manager_id)

        if name:
            business_manager.name = name

        if is_banned is not None:
            business_manager.is_banned = is_banned

        business_manager.save()
        return business_manager

    def count(self):
        return BusinessManager.select(fn.count(BusinessManager.id)).scalar()

    def bind_executor(self, business_manager_id, executor_id):
        executor = self.executor_service.get(executor_id)
        business_manager = self.get(business_manager_id)

        business_manager.executors.add(executor)
        business_manager.save()

        return business_manager

    def unbind_executor(self, business_manager_id, executor_id):
        executor = self.executor_service.get(executor_id)
        business_manager = self.get(business_manager_id)

        business_manager.executors.remove(executor)
        business_manager.save()

        return business_manager


@service
class AdCabinetService:
    def __init__(self, business_manager_service: BusinessManagerService):
        self.business_manager_service = business_manager_service

    def get(self, id):
        return AdCabinet.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(AdCabinet, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [ac for ac in AdCabinet.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name, is_banned):
        ad_cabinet = AdCabinet(name=name, is_banned=is_banned)
        ad_cabinet.save()
        return ad_cabinet

    def update(self, ad_cabinet_id, name=None, is_banned=None):
        ad_cabinet = AdCabinet.get_by_id(ad_cabinet_id)

        if name:
            ad_cabinet.name = name

        if is_banned is not None:
            ad_cabinet.is_banned = is_banned

        ad_cabinet.save()
        return ad_cabinet

    def count(self):
        return AdCabinet.select(fn.count(AdCabinet.id)).scalar()

    def bind_business_manager(self, ad_cabinet_id, business_manager_id):
        business_manager = self.business_manager_service.get(business_manager_id)
        ad_cabinet = self.get(ad_cabinet_id)

        ad_cabinet.business_manager_id = business_manager.id
        ad_cabinet.save()

        return ad_cabinet

    def unbind_business_manager(self, ad_cabinet_id, business_manager_id):
        ad_cabinet = self.get(ad_cabinet_id)
        if ad_cabinet.business_manager_id != business_manager_id:
            raise exceptions.BadBusinessManagerError()

        ad_cabinet.business_manager_id = None
        ad_cabinet.save()


class CampaignService:
    def __init__(
        self,
        ad_cabinet_service: AdCabinetService,
        executor_service: ExecutorService,
        core_campaign_service: CoreCampaignService,
    ):
        self.ad_cabinet_service = ad_cabinet_service
        self.executor_service = executor_service
        self.core_campaign_service = core_campaign_service

    def get(self, id):
        return Campaign.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(Campaign, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [ac for ac in Campaign.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name, cost_value, currency, ad_cabinet_id, executor_id):
        core_campaign = self.core_campaign_service.create(name, CostModel.cpa.value, cost_value, currency)

        ad_cabinet = self.ad_cabinet_service.get(ad_cabinet_id)
        executor = self.executor_service.get(executor_id)

        campaign = Campaign(core_campaign=core_campaign, ad_cabinet=ad_cabinet, executor=executor)
        campaign.save()
        return campaign

    def update(self, campaign_id, name=None, cost_value=None, currency=None, ad_cabinet_id=None, executor_id=None):
        campaign = self.get(campaign_id)

        self.core_campaign_service.update(campaign.core_campaign.id, name, cost_value, currency)

        if ad_cabinet_id:
            ad_cabinet = self.ad_cabinet_service.get(ad_cabinet_id)
            campaign.ad_cabinet = ad_cabinet

        if executor_id:
            executor = self.executor_service.get(executor_id)
            campaign.executor = executor

        campaign.save()
        return campaign

    def count(self):
        return Campaign.select(fn.count(Campaign.id)).scalar()
