from datetime import datetime, timezone


def camelcase(s):
    parts = iter(s.split('_'))
    return next(parts) + ''.join(i.title() for i in parts)


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)
