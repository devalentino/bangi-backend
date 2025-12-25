from wireup import service

from peewee import fn
from src.core.enums import SortOrder
from src.facebook_autoregs.entities import Executor


@service
class ExecutorService:
    def get(self, id):
        return Executor.get_by_id(id)

    def list(self, page, page_size, sort_by, sort_order):
        order_by = getattr(Executor, sort_by)
        if sort_order == SortOrder.desc:
            order_by = order_by.desc()

        return [c for c in Executor.select().order_by(order_by).limit(page_size).offset(page - 1)]

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
