"""Peewee migrations -- 006_campaign_status_mapper_and_postback_fields.py."""

import decimal
from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    migrator.add_fields(
        'campaign',
        status_mapper=pw.TextField(null=True),
    )

    migrator.add_fields(
        'track_postback',
        status=pw.CharField(max_length=255, null=True),
        cost_value=pw.DecimalField(
            auto_round=False,
            decimal_places=5,
            max_digits=10,
            null=True,
            rounding=decimal.ROUND_DOWN,
        ),
        currency=pw.CharField(max_length=255, null=True),
    )


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    migrator.remove_fields('track_postback', 'status', 'cost_value', 'currency')
    migrator.remove_fields('campaign', 'status_mapper')
