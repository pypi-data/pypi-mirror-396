"""__init__ module."""

import logging
from pathlib import Path

import django
import django_stubs_ext
from django.conf import settings

logger = logging.getLogger(__name__)

django_stubs_ext.monkeypatch()
logger.info("Monkeypatched django-stubs")


logger = logging.getLogger(__name__)


# Configure Django settings for tests if not already configured
if not settings.configured:
    logger.info("Configuring minimal django settings for tests")
    installed_apps = ["tests"] if Path("tests").exists() else []
    settings.configure(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=installed_apps,
        USE_TZ=True,
    )
    django.setup()
    logger.info("Django setup complete")
