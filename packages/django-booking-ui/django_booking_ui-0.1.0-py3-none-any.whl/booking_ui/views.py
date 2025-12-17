import datetime as dt

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .conf import booking_settings
from .forms import BookingDetailsForm, PortalLookupForm, RescheduleForm
from .utils import (
    call_callable_with_supported_kwargs,
    filter_for_tenant,
    get_callable,
    get_model,
    parse_slot_string,
    prepare_addon_choices,
    timezone_from_setting,
)


def _require_tenant(tenant_slug):
    if not booking_settings.TENANT_MODEL:
        return None
    if not tenant_slug:
        raise Http404("Tenant not provided.")
    tenant_model = get_model(booking_settings.TENANT_MODEL, "tenant")
    return get_object_or_404(tenant_model, slug=tenant_slug)


def _reverse(name, tenant):
    kwargs = {}
    if booking_settings.TENANT_MODEL:
        kwargs["tenant_slug"] = getattr(tenant, "slug", tenant)
    return reverse(name, kwargs=kwargs or None)


def _get_service_queryset(tenant=None):
    service_model = get_model(booking_settings.SERVICE_MODEL, "service")
    qs = service_model.objects.all()
    field_names = {f.name for f in service_model._meta.fields}
    if "is_active" in field_names:
        qs = qs.filter(is_active=True)
    if "public" in field_names:
        qs = qs.filter(public=True)
    qs = filter_for_tenant(qs, tenant)
    return qs


def _get_service(service_slug, tenant=None):
    qs = _get_service_queryset(tenant)
    lookup = {"slug": service_slug} if "slug" in [f.name for f in qs.model._meta.fields] else {"pk": service_slug}
    return get_object_or_404(qs, **lookup)


def _provider_queryset(service=None, tenant=None):
    provider_model = get_model(booking_settings.PROVIDER_MODEL, "provider")
    qs = provider_model.objects.all()
    field_names = {f.name for f in provider_model._meta.fields}
    if "is_active" in field_names:
        qs = qs.filter(is_active=True)
    if service is not None:
        if hasattr(service, "providers"):
            qs = service.providers.all()
        elif "service" in field_names:
            qs = qs.filter(service=service)
        elif "services" in field_names:
            qs = qs.filter(services=service)
    qs = filter_for_tenant(qs, tenant)
    return qs


def _get_booking_model():
    return get_model(booking_settings.BOOKING_MODEL, "booking")


def _get_booking_for_reference(reference, tenant=None):
    booking_model = _get_booking_model()
    qs = booking_model.objects.all()
    qs = filter_for_tenant(qs, tenant)
    lookup_fields = ["reference", "code"]
    for field in lookup_fields:
        if field in [f.name for f in booking_model._meta.fields]:
            return qs.filter(**{field: reference}).first()
    return None


def _booking_email(booking):
    for field in ["email", "client_email", "customer_email"]:
        if hasattr(booking, field):
            return getattr(booking, field)
    return None


def _booking_can_cancel(booking):
    allowed = getattr(booking, "can_cancel", None)
    return allowed() if callable(allowed) else bool(getattr(booking, "can_cancel", True))


def _booking_can_reschedule(booking):
    allowed = getattr(booking, "can_reschedule", None)
    return allowed() if callable(allowed) else bool(getattr(booking, "can_reschedule", True))


def home(request, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    return redirect(_reverse("booking_ui_services", tenant))


def services_list(request, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    services = _get_service_queryset(tenant)
    categories = {}
    for service in services:
        category = getattr(service, "category", None)
        categories.setdefault(category or "Other", []).append(service)
    context = {
        "tenant": tenant,
        "categories": categories,
        "branding": booking_settings.BRANDING,
    }
    return render(request, "booking_ui/services_list.html", context)


def service_detail(request, service_slug, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    service = _get_service(service_slug, tenant)
    providers = _provider_queryset(service, tenant)
    provider = providers.first() if providers.count() == 1 else None
    if provider and request.method == "GET":
        return redirect(
            reverse(
                "booking_ui_schedule_provider",
                kwargs={
                    **({"tenant_slug": tenant.slug} if tenant else {}),
                    "service_slug": service_slug,
                    "provider_slug": getattr(provider, "slug", provider.pk),
                },
            )
        )
    context = {
        "tenant": tenant,
        "service": service,
        "providers": providers,
        "branding": booking_settings.BRANDING,
    }
    return render(request, "booking_ui/service_detail.html", context)


def service_providers(request, service_slug, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    service = _get_service(service_slug, tenant)
    providers = _provider_queryset(service, tenant)
    if providers.count() == 1:
        provider = providers.first()
        return redirect(
            reverse(
                "booking_ui_schedule_provider",
                kwargs={
                    **({"tenant_slug": tenant.slug} if tenant else {}),
                    "service_slug": service_slug,
                    "provider_slug": getattr(provider, "slug", provider.pk),
                },
            )
        )
    return render(
        request,
        "booking_ui/service_detail.html",
        {
            "tenant": tenant,
            "service": service,
            "providers": providers,
            "branding": booking_settings.BRANDING,
        },
    )


def schedule(request, service_slug, provider_slug=None, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    service = _get_service(service_slug, tenant)
    providers = _provider_queryset(service, tenant)
    provider = None
    if provider_slug:
        provider = get_object_or_404(
            providers,
            **(
                {"slug": provider_slug}
                if "slug" in [f.name for f in providers.model._meta.fields]
                else {"pk": provider_slug}
            ),
        )

    tz = timezone_from_setting()
    start_date = timezone.localdate()
    start_dt = timezone.make_aware(dt.datetime.combine(start_date, dt.time.min), timezone=tz)
    end_dt = start_dt + dt.timedelta(days=booking_settings.DATE_RANGE_DAYS)

    slots_func = get_callable("SLOTS_FUNC", "slot retrieval")
    slots = call_callable_with_supported_kwargs(
        slots_func,
        service=service,
        provider=provider,
        start=start_dt,
        end=end_dt,
        request=request,
        tenant=tenant,
    )

    grouped_slots = {}
    for slot in slots or []:
        start = getattr(slot, "start", None) or getattr(slot, "begin", None)
        end = getattr(slot, "end", None) or getattr(slot, "finish", None)
        if start is None and isinstance(slot, dict):
            start = slot.get("start") or slot.get("begin")
            end = slot.get("end") or slot.get("finish")
        if start is None:
            continue
        if isinstance(start, str):
            start = parse_slot_string(start, tz)
        if not start:
            continue
        start_local = timezone.localtime(start, tz)
        date_key = start_local.date()
        grouped_slots.setdefault(date_key, []).append({"start": start_local, "end": end})

    context = {
        "tenant": tenant,
        "service": service,
        "provider": provider,
        "providers": providers,
        "grouped_slots": grouped_slots,
        "start_date": start_date,
        "end_date": end_dt.date(),
        "branding": booking_settings.BRANDING,
        "timezone": tz,
        "date_range_days": booking_settings.DATE_RANGE_DAYS,
    }
    return render(request, "booking_ui/schedule.html", context)


def confirm(request, service_slug, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    service = _get_service(service_slug, tenant)
    provider_slug = request.GET.get("provider") or request.POST.get("provider")
    providers = _provider_queryset(service, tenant)
    provider = None
    if provider_slug:
        provider = providers.filter(slug=provider_slug).first() or providers.filter(pk=provider_slug).first()
        if not provider:
            raise Http404("Provider not found.")
    slot_str = request.GET.get("slot") or request.POST.get("slot")
    tz = timezone_from_setting()
    slot_dt = parse_slot_string(slot_str, tz)
    if not slot_dt:
        return HttpResponseBadRequest("Invalid or missing slot.")

    addon_choices = getattr(service, "addons", None)
    addon_choices = addon_choices.all() if hasattr(addon_choices, "all") else addon_choices
    form = BookingDetailsForm(data=request.POST or None, addon_choices=addon_choices)

    if request.method == "POST" and form.is_valid():
        create_booking = get_callable("CREATE_BOOKING_FUNC", "booking creation")
        payload = {
            "service": service,
            "provider": provider,
            "start": slot_dt,
            "client_name": form.cleaned_data["client_name"],
            "email": form.cleaned_data.get("email"),
            "phone": form.cleaned_data.get("phone"),
            "notes": form.cleaned_data.get("notes"),
            "addons": form.cleaned_data.get("addons") or [],
            "tenant": tenant,
            "request": request,
        }
        booking = call_callable_with_supported_kwargs(create_booking, **payload)
        request.session["booking_reference"] = getattr(booking, "reference", None)
        booking_email = _booking_email(booking) or form.cleaned_data.get("email")
        if booking_email:
            request.session["booking_portal_email"] = booking_email
        request.session["booking_service_slug"] = service_slug
        success_url = reverse(
            "booking_ui_success",
            kwargs={**({"tenant_slug": tenant.slug} if tenant else {}), "service_slug": service_slug},
        )
        return redirect(success_url)

    context = {
        "tenant": tenant,
        "service": service,
        "provider": provider,
        "slot": slot_dt,
        "form": form,
        "branding": booking_settings.BRANDING,
    }
    return render(request, "booking_ui/confirm.html", context)


def success(request, service_slug, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    reference = request.session.get("booking_reference")
    portal_email = request.session.get("booking_portal_email")
    kwargs = {**({"tenant_slug": tenant.slug} if tenant else {})}
    if reference:
        kwargs["reference"] = reference
        portal_url = reverse("booking_ui_portal_detail", kwargs=kwargs)
        if portal_email:
            portal_url += f"?email={portal_email}"
    else:
        portal_url = reverse("booking_ui_portal_lookup", kwargs=kwargs if kwargs else None)
    context = {
        "tenant": tenant,
        "reference": reference,
        "portal_url": portal_url,
        "branding": booking_settings.BRANDING,
    }
    return render(request, "booking_ui/success.html", context)


def portal_lookup(request, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    form = PortalLookupForm(request.POST or None)
    booking = None
    if request.method == "POST" and form.is_valid():
        reference = form.cleaned_data["reference"]
        email = form.cleaned_data["email"]
        booking = _get_booking_for_reference(reference, tenant=tenant)
        if not booking:
            form.add_error(None, "Booking not found.")
        else:
            stored_email = _booking_email(booking)
            if booking_settings.REQUIRE_PORTAL_EMAIL_MATCH and stored_email and stored_email.lower() != email.lower():
                form.add_error(None, "Email does not match this booking.")
                booking = None
            else:
                request.session["booking_portal_email"] = email
                return redirect(
                    reverse(
                        "booking_ui_portal_detail",
                        kwargs={**({"tenant_slug": tenant.slug} if tenant else {}), "reference": reference},
                    )
                    + (f"?email={email}" if email else "")
                )
    return render(
        request,
        "booking_ui/portal_lookup.html",
        {
            "tenant": tenant,
            "form": form,
            "booking": booking,
            "branding": booking_settings.BRANDING,
        },
    )


def portal_detail(request, reference, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    booking = _get_booking_for_reference(reference, tenant=tenant)
    if not booking:
        raise Http404("Booking not found.")
    stored_email = _booking_email(booking)
    if booking_settings.REQUIRE_PORTAL_EMAIL_MATCH and stored_email:
        email = request.GET.get("email") or request.session.get("booking_portal_email")
        if not email or stored_email.lower() != email.lower():
            raise Http404("Booking not available.")
    can_cancel = _booking_can_cancel(booking)
    can_reschedule = _booking_can_reschedule(booking)
    context = {
        "tenant": tenant,
        "booking": booking,
        "can_cancel": can_cancel,
        "can_reschedule": can_reschedule,
        "branding": booking_settings.BRANDING,
    }
    return render(request, "booking_ui/portal_detail.html", context)


def cancel_booking(request, reference, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    booking = _get_booking_for_reference(reference, tenant=tenant)
    if not booking:
        raise Http404("Booking not found.")
    if not _booking_can_cancel(booking):
        raise Http404("Cancellation not permitted.")
    if request.method != "POST":
        return redirect(
            reverse(
                "booking_ui_portal_detail",
                kwargs={**({"tenant_slug": tenant.slug} if tenant else {}), "reference": reference},
            )
        )
    cancel_func = get_callable("CANCEL_FUNC", "booking cancellation")
    call_callable_with_supported_kwargs(cancel_func, booking=booking, request=request, tenant=tenant)
    return redirect(
        reverse(
            "booking_ui_portal_detail",
            kwargs={**({"tenant_slug": tenant.slug} if tenant else {}), "reference": reference},
        )
    )


def reschedule(request, reference, tenant_slug=None):
    tenant = _require_tenant(tenant_slug) if booking_settings.TENANT_MODEL else None
    booking = _get_booking_for_reference(reference, tenant=tenant)
    if not booking:
        raise Http404("Booking not found.")
    if not _booking_can_reschedule(booking):
        raise Http404("Reschedule not permitted.")

    service = getattr(booking, "service", None)
    provider = getattr(booking, "provider", None)
    if service is None:
        raise ImproperlyConfigured("Booking object must expose a service for rescheduling.")

    providers = _provider_queryset(service, tenant)
    selected_provider_slug = request.GET.get("provider") or getattr(provider, "slug", None)
    if selected_provider_slug and providers.filter(slug=selected_provider_slug).exists():
        provider = providers.get(slug=selected_provider_slug)

    tz = timezone_from_setting()
    start_date = timezone.localdate()
    start_dt = timezone.make_aware(dt.datetime.combine(start_date, dt.time.min), timezone=tz)
    end_dt = start_dt + dt.timedelta(days=booking_settings.DATE_RANGE_DAYS)

    slots_func = get_callable("SLOTS_FUNC", "slot retrieval")
    slots = call_callable_with_supported_kwargs(
        slots_func,
        service=service,
        provider=provider,
        start=start_dt,
        end=end_dt,
        request=request,
        tenant=tenant,
    )

    grouped_slots = {}
    for slot in slots or []:
        start = getattr(slot, "start", None) or getattr(slot, "begin", None)
        if start is None and isinstance(slot, dict):
            start = slot.get("start") or slot.get("begin")
        if start is None:
            continue
        if isinstance(start, str):
            start = parse_slot_string(start, tz)
        if not start:
            continue
        start_local = timezone.localtime(start, tz)
        date_key = start_local.date()
        grouped_slots.setdefault(date_key, []).append({"start": start_local})

    form = RescheduleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        slot_str = form.cleaned_data["slot"]
        slot_dt = parse_slot_string(slot_str, tz)
        if not slot_dt:
            form.add_error(None, "Invalid slot selected.")
        else:
            reschedule_func = get_callable("RESCHEDULE_FUNC", "booking reschedule")
            call_callable_with_supported_kwargs(
                reschedule_func,
                booking=booking,
                provider=provider,
                start=slot_dt,
                request=request,
                tenant=tenant,
            )
            return redirect(
                reverse(
                    "booking_ui_portal_detail",
                    kwargs={**({"tenant_slug": tenant.slug} if tenant else {}), "reference": reference},
                )
            )

    return render(
        request,
        "booking_ui/reschedule.html",
        {
            "tenant": tenant,
            "booking": booking,
            "service": service,
            "provider": provider,
            "providers": providers,
            "grouped_slots": grouped_slots,
            "form": form,
            "branding": booking_settings.BRANDING,
        },
    )
