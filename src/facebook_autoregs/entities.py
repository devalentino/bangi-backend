from playhouse.shortcuts import model_to_dict

from peewee import BooleanField, CharField, ForeignKeyField, ManyToManyField
from src.core.entities import Campaign as CoreCampaign
from src.core.entities import Entity

TABLE_NAME_PREFIX = 'facebook_autoregs_'


class Executor(Entity):
    name = CharField()
    is_banned = BooleanField()

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}executor'


class BusinessManager(Entity):
    name = CharField()
    is_banned = BooleanField()
    executors = ManyToManyField(Executor, backref='executors')

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}business_manager'

    def to_dict(self):
        return model_to_dict(self) | {
            'executors': [e.to_dict() for e in self.executors],
            'ad_cabinets': [ac.to_dict() for ac in self.ad_cabinets],
        }


class AdCabinet(Entity):
    name = CharField()
    is_banned = BooleanField()
    business_manager = ForeignKeyField(BusinessManager, backref='ad_cabinets', null=True)

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}ad_cabinet'

    def to_dict(self):
        business_manager_dict = None
        if self.business_manager:
            business_manager_dict = {
                'id': self.business_manager.id,
                'name': self.business_manager.name,
                'is_banned': self.business_manager.is_banned,
            }

        return model_to_dict(self) | {'business_manager': business_manager_dict}


class Campaign(Entity):
    core_campaign = ForeignKeyField(CoreCampaign, backref='core_campaign')
    ad_cabinet = ForeignKeyField(AdCabinet, backref='ad_cabinet')
    executor = ForeignKeyField(Executor, backref='executor')

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}ad_campaign'


class BusinessManagerAccessLink(Entity):
    business_manager = ForeignKeyField(BusinessManager, backref='access_links', null=True)
    link = CharField()

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}business_manager_access_link'


BusinessManagerExecutor = BusinessManager.executors.get_through_model()
BusinessManagerExecutor._meta.table_name = f'{TABLE_NAME_PREFIX}business_manager2executor'
