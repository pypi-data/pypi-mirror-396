"""
Run the django-booking-ui test suite with a simple command:

    python -m booking_ui.tests
"""

import sys

import django
from django.conf import settings


DEFAULT_SETTINGS = {
    "INSTALLED_APPS": [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "booking_ui",
        "booking_ui.tests",
    ],
    "DATABASES": {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
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
    "SECRET_KEY": "booking-ui-test-secret",
    "USE_TZ": True,
    "STATIC_URL": "/static/",
    "DEFAULT_AUTO_FIELD": "django.db.models.AutoField",
    "BOOKING_UI_SERVICE_MODEL": "tests.Service",
    "BOOKING_UI_PROVIDER_MODEL": "tests.Provider",
    "BOOKING_UI_BOOKING_MODEL": "tests.Booking",
    "BOOKING_UI_SLOTS_FUNC": "booking_ui.tests.utils.fake_slots",
    "BOOKING_UI_CREATE_BOOKING_FUNC": "booking_ui.tests.utils.fake_create_booking",
    "BOOKING_UI_RESCHEDULE_FUNC": "booking_ui.tests.utils.fake_reschedule_booking",
    "BOOKING_UI_CANCEL_FUNC": "booking_ui.tests.utils.fake_cancel_booking",
    "BOOKING_UI_DATE_RANGE_DAYS": 14,
    "MIGRATION_MODULES": {"booking_ui.tests": None},
}


def main():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    django.setup()
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["booking_ui"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
