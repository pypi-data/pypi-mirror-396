from unittest import skipIf, skipUnless

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase

from providers import conf, selectors
from providers.models import Provider, ProviderService


@skipIf(conf.tenant_enabled(), "Requires tenancy disabled")
class ProviderSlugTests(TestCase):
    def test_slug_auto_increment_global(self):
        first = Provider.objects.create(
            name="Alpha Tutor", provider_type=Provider.ProviderType.PERSON
        )
        second = Provider.objects.create(
            name="Alpha Tutor", provider_type=Provider.ProviderType.PERSON
        )

        self.assertEqual(first.slug, "alpha-tutor")
        self.assertEqual(second.slug, "alpha-tutor-2")

    def test_resource_providers_can_be_disabled(self):
        with self.settings(PROVIDERS_ALLOW_RESOURCE_PROVIDERS=False):
            with self.assertRaises(ValidationError):
                Provider.objects.create(
                    name="Room 1", provider_type=Provider.ProviderType.RESOURCE
                )


@skipIf(conf.tenant_enabled(), "Requires tenancy disabled")
class ProviderServiceTests(TestCase):
    def setUp(self):
        self.provider = Provider.objects.create(
            name="Alex Tutor", provider_type=Provider.ProviderType.PERSON
        )
        from providers.tests.services.models import Service

        self.service = Service.objects.create(name="Maths 101", slug="maths-101")

    def test_provider_service_mapping(self):
        link = ProviderService.objects.create(
            provider=self.provider, service=self.service
        )
        self.assertTrue(link.is_active)
        self.assertEqual(link.priority, 0)

    def test_duplicate_provider_service_blocked(self):
        ProviderService.objects.create(provider=self.provider, service=self.service)
        with self.assertRaises(ValidationError):
            duplicate = ProviderService(
                provider=self.provider, service=self.service, priority=1
            )
            duplicate.full_clean()

    def test_selectors_in_single_tenant_mode(self):
        link = ProviderService.objects.create(
            provider=self.provider, service=self.service
        )
        providers = selectors.list_providers()
        self.assertIn(self.provider, providers)
        fetched = selectors.get_provider(slug=self.provider.slug)
        self.assertEqual(fetched, self.provider)

        services = selectors.list_services_for_provider(self.provider)
        self.assertEqual([link.service], services)

        providers_for_service = selectors.list_providers_for_service(self.service)
        self.assertEqual([self.provider], providers_for_service)

    def test_tenant_parameter_disallowed_when_unset(self):
        with self.assertRaises(ImproperlyConfigured):
            selectors.list_providers(tenant=object())


@skipUnless(conf.tenant_enabled(), "Requires tenancy enabled")
class TenantAwareProviderTests(TestCase):
    def setUp(self):
        from providers.tests.tenants.models import Tenant
        from providers.tests.services.models import Service

        self.tenant_a = Tenant.objects.create(name="Tenant A")
        self.tenant_b = Tenant.objects.create(name="Tenant B")

        self.provider_a = Provider.objects.create(
            name="Alex",
            provider_type=Provider.ProviderType.PERSON,
            tenant=self.tenant_a,
        )
        self.provider_b = Provider.objects.create(
            name="Alex",
            provider_type=Provider.ProviderType.PERSON,
            tenant=self.tenant_b,
        )
        self.service_a = Service.objects.create(
            name="Maths", slug="maths", tenant=self.tenant_a
        )
        self.service_b = Service.objects.create(
            name="Science", slug="science", tenant=self.tenant_b
        )

    def test_slug_unique_per_tenant(self):
        self.assertEqual(self.provider_a.slug, "alex")
        self.assertEqual(self.provider_b.slug, "alex")
        clash = Provider.objects.create(
            name="Alex", provider_type=Provider.ProviderType.PERSON, tenant=self.tenant_a
        )
        self.assertEqual(clash.slug, "alex-2")

    def test_tenant_consistency_enforced(self):
        link = ProviderService(
            provider=self.provider_a,
            service=self.service_b,
            tenant=self.tenant_a,
        )
        with self.assertRaises(ValidationError):
            link.full_clean()

    def test_selector_filters_by_tenant(self):
        ProviderService.objects.create(
            provider=self.provider_a, service=self.service_a, tenant=self.tenant_a
        )
        ProviderService.objects.create(
            provider=self.provider_b, service=self.service_b, tenant=self.tenant_b
        )

        tenant_a_providers = selectors.list_providers(tenant=self.tenant_a)
        self.assertEqual(list(tenant_a_providers), [self.provider_a])

        services = selectors.list_services_for_provider(self.provider_a)
        self.assertEqual(services, [self.service_a])

        providers_for_service = selectors.list_providers_for_service(self.service_b)
        self.assertEqual(providers_for_service, [self.provider_b])


@skipIf(conf.tenant_enabled(), "Requires tenancy disabled")
class ProviderUserLinkTests(TestCase):
    def test_provider_can_link_to_user(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="alex", email="alex@example.com", password="secret"
        )
        provider = Provider.objects.create(
            name="Alex Tutor",
            provider_type=Provider.ProviderType.PERSON,
            user=user,
        )
        self.assertEqual(provider.user, user)
