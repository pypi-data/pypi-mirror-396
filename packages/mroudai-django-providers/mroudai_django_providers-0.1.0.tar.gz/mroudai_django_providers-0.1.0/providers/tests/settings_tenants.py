import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "test-secret-key"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "providers.tests.services",
    "providers.tests.tenants",
    "providers",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

PROVIDERS_TENANT_MODEL = "tenants.Tenant"
