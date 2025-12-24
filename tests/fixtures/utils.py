from datetime import datetime, timezone

import pytest


@pytest.fixture
def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@pytest.fixture
def timestamp(utcnow):
    return int(utcnow.timestamp())
