
from __future__ import absolute_import

from django.conf import settings

DEFAULT_SETTINGS = dict(
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
    MIDDLEWARE_CLASSES=[],
)


def configure(**kwargs):
    config = dict(DEFAULT_SETTINGS)
    config.update(kwargs)
    settings.configure(**config)
