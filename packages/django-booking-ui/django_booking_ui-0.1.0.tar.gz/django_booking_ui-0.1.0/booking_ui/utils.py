import datetime as _dt
from typing import Any, Iterable, Optional

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.module_loading import import_string

from .conf import booking_settings


def get_callable(setting_name: str, description: str):
    """
    Import a callable from a dotted path defined in settings.

    Parameters
    ----------
    setting_name: str
        The upper-case suffix after BOOKING_UI_ (e.g. ``SLOTS_FUNC``).
    description: str
        Human friendly description for error messages.
    """
    dotted_path = getattr(booking_settings, setting_name, None)
    if not dotted_path:
        raise ImproperlyConfigured(
            f"BOOKING_UI_{setting_name} must be set to a dotted path for {description}."
        )
    try:
        return import_string(dotted_path)
    except Exception as exc:  # pragma: no cover - defensive
        raise ImproperlyConfigured(
            f"Could not import BOOKING_UI_{setting_name} ({dotted_path}) for {description}: {exc}"
        ) from exc


def get_model(dotted_path: str, description: str):
    try:
        return apps.get_model(dotted_path, require_ready=False)
    except Exception as exc:
        raise ImproperlyConfigured(
            f"Could not import {description} model '{dotted_path}': {exc}"
        ) from exc


def filter_for_tenant(queryset, tenant):
    """Filter a queryset by tenant if the model exposes a tenant field."""
    if not tenant:
        return queryset
    model = queryset.model
    field_names = {f.name for f in model._meta.fields}
    if "tenant" in field_names:
        return queryset.filter(tenant=tenant)
    if "organisation" in field_names:
        return queryset.filter(organisation=tenant)
    if "account" in field_names:
        return queryset.filter(account=tenant)
    return queryset


def parse_slot_string(value: str, tz) -> Optional[_dt.datetime]:
    """Parse ISO slot strings into aware datetimes."""
    if not value:
        return None
    value = value.replace(" ", "+")
    try:
        dt = _dt.datetime.fromisoformat(value)
    except ValueError:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone=tz)
    return dt.astimezone(tz)


def timezone_from_setting():
    tz_setting = booking_settings.DEFAULT_TIMEZONE
    if tz_setting is None:
        return timezone.get_current_timezone()
    if isinstance(tz_setting, str):
        try:
            try:
                from zoneinfo import ZoneInfo

                return ZoneInfo(tz_setting)
            except Exception:
                if hasattr(timezone, "pytz"):
                    return timezone.pytz.timezone(tz_setting)
        except Exception as exc:  # pragma: no cover
            raise ImproperlyConfigured(
                f"BOOKING_UI_DEFAULT_TIMEZONE '{tz_setting}' is not valid: {exc}"
            ) from exc
    if isinstance(tz_setting, int):
        return timezone.get_fixed_timezone(tz_setting)
    return tz_setting


def choice_from_queryset(qs, value) -> Optional[Any]:
    if value is None:
        return None
    try:
        return qs.get(pk=value)
    except Exception:
        return None


def prepare_addon_choices(addons: Iterable[Any]) -> list[tuple]:
    choices = []
    for addon in addons or []:
        label = getattr(addon, "name", str(addon))
        choices.append((getattr(addon, "pk", label), label))
    return choices


def call_callable_with_supported_kwargs(func, **kwargs):
    """Call a callable only with the kwargs it accepts."""
    try:
        from inspect import Parameter, signature

        sig = signature(func)
        if any(p.kind == Parameter.VAR_KEYWORD for p in sig.parameters.values()):
            return func(**kwargs)
        allowed = {name for name in sig.parameters.keys()}
    except Exception:  # pragma: no cover - fallback for dynamic callables
        allowed = kwargs.keys()
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed}
    return func(**filtered_kwargs)
