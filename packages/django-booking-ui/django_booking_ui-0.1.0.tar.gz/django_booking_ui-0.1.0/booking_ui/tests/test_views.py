import datetime as dt

from django.test import TestCase, override_settings
from django.utils import timezone

from booking_ui.tests import utils
from booking_ui.tests.models import Booking, Provider, Service


TEST_SETTINGS = {
    "INSTALLED_APPS": [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "booking_ui",
        "booking_ui.tests",
    ],
    "MIDDLEWARE": [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ],
    "ROOT_URLCONF": "booking_ui.urls",
    "TEMPLATES": [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ],
    "SECRET_KEY": "test-secret",
    "USE_TZ": True,
    "ALLOWED_HOSTS": ["testserver"],
    "BOOKING_UI_SERVICE_MODEL": "tests.Service",
    "BOOKING_UI_PROVIDER_MODEL": "tests.Provider",
    "BOOKING_UI_BOOKING_MODEL": "tests.Booking",
    "BOOKING_UI_TENANT_MODEL": None,
    "BOOKING_UI_SLOTS_FUNC": "booking_ui.tests.utils.fake_slots",
    "BOOKING_UI_CREATE_BOOKING_FUNC": "booking_ui.tests.utils.fake_create_booking",
    "BOOKING_UI_RESCHEDULE_FUNC": "booking_ui.tests.utils.fake_reschedule_booking",
    "BOOKING_UI_CANCEL_FUNC": "booking_ui.tests.utils.fake_cancel_booking",
    "BOOKING_UI_DATE_RANGE_DAYS": 14,
    "MIGRATION_MODULES": {"booking_ui.tests": None},
    "DEFAULT_AUTO_FIELD": "django.db.models.AutoField",
    "STATIC_URL": "/static/",
}


@override_settings(**TEST_SETTINGS)
class BookingUIViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service = Service.objects.create(
            name="Consultation",
            slug="consultation",
            description="Initial call",
            duration=30,
            price=50,
        )
        cls.provider = Provider.objects.create(
            name="Alice", slug="alice", description="Senior", service=cls.service
        )

    def setUp(self):
        utils.reset_calls()

    def test_services_list_shows_active_services(self):
        inactive = Service.objects.create(
            name="Hidden", slug="hidden", description="Inactive", is_active=False
        )
        response = self.client.get("/book/services/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.name)
        self.assertNotContains(response, inactive.name)

    def test_schedule_calls_slots_function(self):
        url = f"/book/services/{self.service.slug}/schedule/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("slots", utils.last_calls)
        self.assertEqual(utils.last_calls["slots"]["service"], self.service)

    def test_confirm_post_creates_booking_and_redirects(self):
        slot = (timezone.now() + dt.timedelta(days=1)).replace(microsecond=0).isoformat()
        url = f"/book/services/{self.service.slug}/confirm/?slot={slot}"
        response = self.client.post(
            url,
            {"client_name": "Test User", "email": "user@example.com", "phone": "", "notes": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/book/services/{self.service.slug}/success/", response["Location"])
        self.assertEqual(utils.last_calls["create_booking"]["client_name"], "Test User")

    def test_portal_lookup_blocks_wrong_email(self):
        Booking.objects.create(
            reference="REF-1",
            client_name="Bob",
            email="bob@example.com",
            service=self.service,
            provider=self.provider,
        )
        response = self.client.post("/book/portal/", {"reference": "REF-1", "email": "wrong@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email does not match this booking.")

    def test_cancel_and_reschedule_enforce_rules(self):
        cannot_cancel = Booking.objects.create(
            reference="NO-CANCEL",
            client_name="Casey",
            email="casey@example.com",
            service=self.service,
            provider=self.provider,
            allow_cancel=False,
        )
        response = self.client.post("/book/portal/NO-CANCEL/cancel/")
        self.assertEqual(response.status_code, 404)

        booking = Booking.objects.create(
            reference="MOVE",
            client_name="Move Me",
            email="move@example.com",
            service=self.service,
            provider=self.provider,
            allow_reschedule=True,
        )
        slot = (timezone.now() + dt.timedelta(days=2)).replace(microsecond=0).isoformat()
        response = self.client.post(f"/book/portal/{booking.reference}/reschedule/", {"slot": slot})
        self.assertEqual(response.status_code, 302)
        self.assertIn("reschedule", utils.last_calls)
        self.assertEqual(utils.last_calls["reschedule"]["booking"], booking)
