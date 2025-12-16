from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from providers import conf

TENANT_MODEL = conf.get_tenant_model()
TENANCY_ENABLED = bool(TENANT_MODEL)


def _metadata_default():
    return {}


class Provider(models.Model):
    class ProviderType(models.TextChoices):
        PERSON = "person", "Person"
        RESOURCE = "resource", "Resource"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        INTERNAL = "internal", "Internal"

    if TENANCY_ENABLED:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="providers",
            db_index=True,
        )

    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        db_index=True,
    )
    provider_type = models.CharField(
        max_length=20,
        choices=ProviderType.choices,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    sort_order = models.IntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="providers",
    )
    metadata = models.JSONField(default=_metadata_default, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name", "pk"]
        indexes = [
            models.Index(
                fields=["is_active", "visibility"],
                name="prov_active_vis_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"] if not TENANCY_ENABLED else ["tenant", "slug"],
                name="providers_provider_slug_unique",
            )
        ]
        if TENANCY_ENABLED:
            indexes.append(
                models.Index(
                    fields=["tenant", "is_active", "sort_order"],
                    name="prov_tenant_active_order_idx",
                )
            )

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}

        if (
            self.provider_type == Provider.ProviderType.RESOURCE
            and not conf.allow_resource_providers()
        ):
            errors["provider_type"] = ValidationError(
                "Resource providers are disabled by settings."
            )

        if errors:
            raise ValidationError(errors)

    def _generate_unique_slug(self, base_slug):
        base_slug = slugify(base_slug or self.name) or "provider"
        slug = base_slug
        existing = Provider.objects.all()
        if TENANCY_ENABLED:
            existing = existing.filter(tenant=self.tenant)
        counter = 2
        while existing.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        base_slug = self.slug or self.name
        self.slug = self._generate_unique_slug(base_slug)
        self.full_clean()
        super().save(*args, **kwargs)


class ProviderService(models.Model):
    if TENANCY_ENABLED:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="provider_services",
            db_index=True,
        )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="provider_services",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="provider_services",
    )
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ["priority", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "service"],
                name="providers_providerservice_unique",
            )
        ]
        if TENANCY_ENABLED:
            indexes = [
                models.Index(
                    fields=["tenant", "priority"],
                    name="provsvc_tenant_priority_idx",
                )
            ]
        else:
            indexes = [
                models.Index(
                    fields=["priority"],
                    name="provsvc_priority_idx",
                )
            ]

    def __str__(self):
        return f"{self.provider} -> {self.service}"

    def clean(self):
        errors = {}

        if TENANCY_ENABLED:
            provider_tenant_id = getattr(self.provider, "tenant_id", None)
            service_tenant_id = getattr(self.service, "tenant_id", None)

            if provider_tenant_id != service_tenant_id:
                errors["service"] = ValidationError(
                    "Provider and service must belong to the same tenant."
                )

            if (
                hasattr(self, "tenant_id")
                and provider_tenant_id
                and self.tenant_id != provider_tenant_id
            ):
                errors["tenant"] = ValidationError(
                    "ProviderService tenant must match provider tenant."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if TENANCY_ENABLED and hasattr(self, "tenant_id") and not self.tenant_id:
            self.tenant = getattr(self.provider, "tenant", None)
        self.full_clean()
        super().save(*args, **kwargs)


class ProviderImage(models.Model):
    if TENANCY_ENABLED:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="provider_images",
            db_index=True,
        )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="providers/images/")
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["sort_order", "pk"]
        indexes = [
            models.Index(
                fields=["sort_order"],
                name="provimg_sort_idx",
            )
        ]

    def __str__(self):
        return f"Image for {self.provider}"

    def clean(self):
        if TENANCY_ENABLED and hasattr(self, "tenant"):
            provider_tenant = getattr(self.provider, "tenant_id", None)
            if provider_tenant and self.tenant_id != provider_tenant:
                raise ValidationError(
                    {"tenant": "ProviderImage tenant must match provider tenant."}
                )

    def save(self, *args, **kwargs):
        if TENANCY_ENABLED and hasattr(self, "tenant_id") and not self.tenant_id:
            self.tenant = getattr(self.provider, "tenant", None)
        self.full_clean()
        super().save(*args, **kwargs)
