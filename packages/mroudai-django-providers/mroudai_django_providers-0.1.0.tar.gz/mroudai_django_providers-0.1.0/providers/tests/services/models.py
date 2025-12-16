from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


TENANT_MODEL = getattr(settings, "PROVIDERS_TENANT_MODEL", None)
TENANCY_ENABLED = bool(TENANT_MODEL)


class Service(models.Model):
    if TENANCY_ENABLED:
        tenant = models.ForeignKey(
            TENANT_MODEL,
            on_delete=models.CASCADE,
            related_name="services",
        )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        app_label = "services"
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"] if not TENANCY_ENABLED else ["tenant", "slug"],
                name="services_service_slug_unique",
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
