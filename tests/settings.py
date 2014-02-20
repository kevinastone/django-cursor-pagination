
from __future__ import absolute_import

from django.conf import settings

settings.configure(
    DEBUG=True,
    USE_TZ=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sites",
        "cursor_pagination",
        "tests",
    ],
    SITE_ID=1,
    NOSE_ARGS=['-s', '--logging-filter=tests,cursor_pagination'],
)
