from django.core.exceptions import ImproperlyConfigured

from providers import conf
from providers.models import Provider, ProviderService


def _enforce_tenant_parameter(tenant):
    if tenant is not None and not conf.tenant_enabled():
        raise ImproperlyConfigured(
            "Tenant parameter supplied but PROVIDERS_TENANT_MODEL is not configured."
        )


def list_providers(*, tenant=None, include_inactive: bool = False, provider_type=None):
    _enforce_tenant_parameter(tenant)

    qs = Provider.objects.all()
    if conf.tenant_enabled() and tenant is not None:
        qs = qs.filter(tenant=tenant)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    if provider_type:
        qs = qs.filter(provider_type=provider_type)
    return qs.order_by("sort_order", "name")


def get_provider(*, slug: str, tenant=None, include_inactive: bool = False):
    _enforce_tenant_parameter(tenant)

    qs = Provider.objects.all()
    if conf.tenant_enabled() and tenant is not None:
        qs = qs.filter(tenant=tenant)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return qs.get(slug=slug)


def list_services_for_provider(provider: Provider, include_inactive: bool = False):
    qs = ProviderService.objects.filter(provider=provider)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    links = qs.select_related("service").order_by("priority", "pk")
    return [link.service for link in links]


def list_providers_for_service(service, include_inactive: bool = False):
    qs = ProviderService.objects.filter(service=service)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    links = qs.select_related("provider").order_by("priority", "pk")
    return [link.provider for link in links]
