from peewee import CharField
from src.core.entities import BaseModel

TABLE_NAME_PREFIX = 'facebook_autoregs_'


class Executor(BaseModel):
    name = CharField()

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}executor'


class AdCabinet(BaseModel):
    name = CharField()

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}ad_cabinet'


class BusinessManager(BaseModel):
    name = CharField()

    class Meta:
        table_name = f'{TABLE_NAME_PREFIX}business_manager'
