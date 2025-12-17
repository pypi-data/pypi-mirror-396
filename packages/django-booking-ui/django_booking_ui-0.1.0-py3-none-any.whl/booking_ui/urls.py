from django.urls import path

from . import views
from .conf import booking_settings

prefix = "book/"
if booking_settings.TENANT_MODEL:
    prefix = "t/<slug:tenant_slug>/book/"

urlpatterns = [
    path(prefix, views.home, name="booking_ui_home"),
    path(f"{prefix}services/", views.services_list, name="booking_ui_services"),
    path(
        f"{prefix}services/<slug:service_slug>/",
        views.service_detail,
        name="booking_ui_service_detail",
    ),
    path(
        f"{prefix}services/<slug:service_slug>/providers/",
        views.service_providers,
        name="booking_ui_service_providers",
    ),
    path(
        f"{prefix}services/<slug:service_slug>/schedule/",
        views.schedule,
        name="booking_ui_schedule",
    ),
    path(
        f"{prefix}services/<slug:service_slug>/schedule/<slug:provider_slug>/",
        views.schedule,
        name="booking_ui_schedule_provider",
    ),
    path(
        f"{prefix}services/<slug:service_slug>/confirm/",
        views.confirm,
        name="booking_ui_confirm",
    ),
    path(
        f"{prefix}services/<slug:service_slug>/success/",
        views.success,
        name="booking_ui_success",
    ),
    path(
        f"{prefix}portal/",
        views.portal_lookup,
        name="booking_ui_portal_lookup",
    ),
    path(
        f"{prefix}portal/<str:reference>/",
        views.portal_detail,
        name="booking_ui_portal_detail",
    ),
    path(
        f"{prefix}portal/<str:reference>/cancel/",
        views.cancel_booking,
        name="booking_ui_cancel_booking",
    ),
    path(
        f"{prefix}portal/<str:reference>/reschedule/",
        views.reschedule,
        name="booking_ui_reschedule",
    ),
]
