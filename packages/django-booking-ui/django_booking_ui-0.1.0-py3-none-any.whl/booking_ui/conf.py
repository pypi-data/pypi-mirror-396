"""
Settings wrapper for django-booking-ui.

Values are lazily pulled from Django settings with sensible defaults.
"""

from django.conf import settings
from django.utils import timezone


class BookingUISettings:
    defaults = {
        "TENANT_MODEL": None,
        "SERVICE_MODEL": "services.Service",
        "PROVIDER_MODEL": "providers.Provider",
        "BOOKING_MODEL": "bookings.Booking",
        "SLOTS_FUNC": "slots.selectors.list_available_slots",
        "CREATE_BOOKING_FUNC": "bookings.services.create_booking",
        "RESCHEDULE_FUNC": "bookings.services.reschedule_booking",
        "CANCEL_FUNC": "bookings.services.cancel_booking",
        "DATE_RANGE_DAYS": 30,
        "DEFAULT_TIMEZONE": None,
        "REQUIRE_PORTAL_EMAIL_MATCH": True,
        "BRANDING": {
            "site_name": "Bookings",
            "support_email": "support@example.com",
        },
    }

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(attr)
        return getattr(settings, f"BOOKING_UI_{attr}", self.defaults[attr])

    def get_timezone(self):
        tz = self.DEFAULT_TIMEZONE
        if tz is None:
            return timezone.get_current_timezone()
        if isinstance(tz, int):
            return timezone.get_fixed_timezone(tz)
        if isinstance(tz, str):
            try:
                from zoneinfo import ZoneInfo

                return ZoneInfo(tz)
            except Exception:
                pass
        return tz


booking_settings = BookingUISettings()
