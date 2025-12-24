from decimal import Decimal

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DatabaseProxy,
    DecimalField,
    ForeignKeyField,
    IntegerField,
    Model,
    TimestampField,
)
from src.core.enums import CostModel, Currency

database_proxy = DatabaseProxy()


class BaseModel(Model):
    id = AutoField()
    created_at = TimestampField(null=True, utc=True)

    class Meta:
        database = database_proxy
        legacy_table_names = False


class Campaign(BaseModel):
    name = CharField()
    cost_model = CharField(null=True, default=CostModel.cpa.value)
    cost_value = DecimalField(null=True, default=Decimal('0.00'))
    currency = CharField(null=True, default=Currency.usd.value)


class Flow(BaseModel):
    campaign_id = ForeignKeyField(Campaign)

    order_value = IntegerField(null=False)
    is_enabled = BooleanField(default=True)
    is_deleted = BooleanField(default=False)
