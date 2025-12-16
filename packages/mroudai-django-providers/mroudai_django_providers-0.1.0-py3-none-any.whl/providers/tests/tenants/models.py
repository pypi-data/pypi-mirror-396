from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        app_label = "tenants"
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name
