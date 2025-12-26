from wireup import service

from peewee import fn
from src.core.enums import SortOrder
from src.facebook_autoregs.entities import AdCabinet, BusinessManager, Executor


@service
class ExecutorService:
    def get(self, id):
        return Executor.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(Executor, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [e for e in Executor.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name):
        executor = Executor(name=name)
        executor.save()

    def update(self, id, name=None):
        executor = Executor.get_by_id(id)

        if name:
            executor.name = name

        executor.save()

    def count(self):
        return Executor.select(fn.count(Executor.id)).scalar()


@service
class BusinessManagerService:
    def get(self, id):
        return BusinessManager.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(BusinessManager, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [bm for bm in BusinessManager.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name):
        business_manager = BusinessManager(name=name)
        business_manager.save()

    def update(self, id, name=None):
        business_manager = BusinessManager.get_by_id(id)

        if name:
            business_manager.name = name

        business_manager.save()

    def count(self):
        return BusinessManager.select(fn.count(BusinessManager.id)).scalar()


@service
class AdCabinetService:
    def get(self, id):
        return AdCabinet.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(AdCabinet, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [ac for ac in AdCabinet.select().order_by(order_by).limit(page_size).offset(page - 1)]

    def create(self, name):
        ad_cabinet = AdCabinet(name=name)
        ad_cabinet.save()

    def update(self, id, name=None):
        ad_cabinet = AdCabinet.get_by_id(id)

        if name:
            ad_cabinet.name = name

        ad_cabinet.save()

    def count(self):
        return AdCabinet.select(fn.count(AdCabinet.id)).scalar()
