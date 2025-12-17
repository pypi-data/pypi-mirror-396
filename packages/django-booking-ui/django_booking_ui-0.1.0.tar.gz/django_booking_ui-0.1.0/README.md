# django-booking-ui

Public booking pages and a lightweight customer portal for Django projects that already have booking logic. This package stays UI-only: it renders services, available slots, booking forms, and a simple portal that calls your existing service functions.

## What it does (and does not)
- ✅ Browse services and providers
- ✅ Select date/time from your slot source
- ✅ Confirm bookings via your `create_booking` service
- ✅ Portal: lookup by reference + email, cancel, reschedule
- ✅ Pluggable templates and minimal, responsive styling
- ❌ No payment handling
- ❌ No booking engine logic – you supply slots and booking services

## Quick start
1) Install
```
pip install django-booking-ui
```

2) Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    "booking_ui",
]
```

3) Configure URLs:
```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("", include("booking_ui.urls")),
]
```

4) Configure settings (examples):
```python
BOOKING_UI_SERVICE_MODEL = "services.Service"
BOOKING_UI_PROVIDER_MODEL = "providers.Provider"
BOOKING_UI_SLOTS_FUNC = "slots.selectors.list_available_slots"
BOOKING_UI_CREATE_BOOKING_FUNC = "bookings.services.create_booking"
BOOKING_UI_RESCHEDULE_FUNC = "bookings.services.reschedule_booking"
BOOKING_UI_CANCEL_FUNC = "bookings.services.cancel_booking"
BOOKING_UI_DATE_RANGE_DAYS = 30
BOOKING_UI_REQUIRE_PORTAL_EMAIL_MATCH = True
# Optional
BOOKING_UI_TENANT_MODEL = "tenants.Tenant"
BOOKING_UI_DEFAULT_TIMEZONE = None  # falls back to current timezone
BOOKING_UI_BRANDING = {"site_name": "Bookings", "support_email": "support@example.com"}
BOOKING_UI_BOOKING_MODEL = "bookings.Booking"  # used for portal lookups
```

### URL structure
- Single-tenant: `/book/…`
- Multi-tenant (when `BOOKING_UI_TENANT_MODEL` is set): `/t/<tenant_slug>/book/…`

Routes include services list, service detail, schedule selection, confirm, success, and portal pages for lookup, cancel, and reschedule.

### Template overrides
Templates live under `booking_ui/` (e.g. `templates/booking_ui/base.html`, `schedule.html`, `portal_detail.html`). Override them by creating files with the same path in your project templates directory.

### Integration hooks
- Slot retrieval: `BOOKING_UI_SLOTS_FUNC(service, provider, start, end, ...)` → iterable of slot objects/dicts with a `start` datetime.
- Booking creation: `BOOKING_UI_CREATE_BOOKING_FUNC(**data)` should return a booking with a `reference` attribute.
- Reschedule/cancel: `BOOKING_UI_RESCHEDULE_FUNC(booking, start, ...)` and `BOOKING_UI_CANCEL_FUNC(booking, ...)`.
- Portal lookup uses `BOOKING_UI_BOOKING_MODEL` to fetch by `reference`; email matching enforced when enabled.

### Tests
Run the built-in suite with a single command:
```
python -m booking_ui.tests
```
You can also integrate with your runner of choice (e.g. `python -m pytest booking_ui`).

### Publish to PyPI
- Set credentials (e.g. `TWINE_USERNAME`/`TWINE_PASSWORD` or `TWINE_API_TOKEN`).
- Run:
```
python upload_project.py
```
This installs build/twine if needed, builds the wheel/sdist, and uploads the contents of `dist/`.

## Licence
MIT Licence. See `LICENSE`.
