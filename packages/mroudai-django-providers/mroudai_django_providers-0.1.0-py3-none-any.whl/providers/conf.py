from django.conf import settings


def get_tenant_model():
    return getattr(settings, "PROVIDERS_TENANT_MODEL", None)


def allow_resource_providers():
    return getattr(settings, "PROVIDERS_ALLOW_RESOURCE_PROVIDERS", True)


def tenant_enabled():
    return bool(get_tenant_model())
