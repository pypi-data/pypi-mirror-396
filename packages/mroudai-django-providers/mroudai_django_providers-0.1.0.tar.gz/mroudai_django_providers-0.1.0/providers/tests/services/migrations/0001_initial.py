from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

TENANT_MODEL = getattr(settings, "PROVIDERS_TENANT_MODEL", None)
TENANCY_ENABLED = bool(TENANT_MODEL)


class Migration(migrations.Migration):
    initial = True

    dependencies = []
    if TENANCY_ENABLED:
        dependencies.append(migrations.swappable_dependency(TENANT_MODEL))

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, editable=False),
                ),
            ]
            + (
                [
                    (
                        "tenant",
                        models.ForeignKey(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name="services",
                            to=TENANT_MODEL,
                        ),
                    )
                ]
                if TENANCY_ENABLED
                else []
            ),
            options={
                "ordering": ["name", "pk"],
                "app_label": "services",
            },
        ),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.UniqueConstraint(
                fields=["slug"] if not TENANCY_ENABLED else ["tenant", "slug"],
                name="services_service_slug_unique",
            ),
        ),
    ]
