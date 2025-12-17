import datetime as dt
from types import SimpleNamespace

from django.utils import timezone

last_calls = {}


def reset_calls():
    last_calls.clear()


def fake_slots(service=None, provider=None, start=None, end=None, **kwargs):
    last_calls["slots"] = {"service": service, "provider": provider, "start": start, "end": end}
    base = timezone.now().replace(microsecond=0)
    return [
        SimpleNamespace(start=base + dt.timedelta(days=1, hours=9)),
        SimpleNamespace(start=base + dt.timedelta(days=2, hours=11)),
    ]


def fake_create_booking(**kwargs):
    last_calls["create_booking"] = kwargs
    return SimpleNamespace(
        reference="REF123",
        client_name=kwargs.get("client_name"),
        email=kwargs.get("email"),
        service=kwargs.get("service"),
        provider=kwargs.get("provider"),
        start=kwargs.get("start"),
    )


def fake_reschedule_booking(**kwargs):
    last_calls["reschedule"] = kwargs
    booking = kwargs.get("booking") or SimpleNamespace()
    booking.start = kwargs.get("start")
    return booking


def fake_cancel_booking(**kwargs):
    last_calls["cancel"] = kwargs
    return kwargs.get("booking")
