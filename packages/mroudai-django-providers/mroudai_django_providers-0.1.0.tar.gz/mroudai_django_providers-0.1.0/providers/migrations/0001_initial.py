from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

from providers import conf

TENANT_MODEL = conf.get_tenant_model()
TENANCY_ENABLED = bool(TENANT_MODEL)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("services", "__first__"),
    ]
    if TENANCY_ENABLED:
        dependencies.append(migrations.swappable_dependency(TENANT_MODEL))

    operations = [
        migrations.CreateModel(
            name="Provider",
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
            ],
            options={
                "ordering": ["sort_order", "name", "pk"],
            },
        ),
    ]

    if TENANCY_ENABLED:
        operations[0].fields.append(
            (
                "tenant",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="providers",
                    to=TENANT_MODEL,
                    db_index=True,
                ),
            )
        )

    operations[0].fields.extend(
        [
            ("name", models.CharField(max_length=255)),
            (
                "slug",
                models.SlugField(
                    max_length=255,
                    db_index=True,
                ),
            ),
            (
                "provider_type",
                models.CharField(
                    choices=[("person", "Person"), ("resource", "Resource")],
                    max_length=20,
                ),
            ),
            ("description", models.TextField(blank=True)),
            ("is_active", models.BooleanField(default=True)),
            (
                "visibility",
                models.CharField(
                    choices=[("public", "Public"), ("internal", "Internal")],
                    default="public",
                    max_length=20,
                ),
            ),
            ("sort_order", models.IntegerField(default=0)),
            (
                "metadata",
                models.JSONField(default=dict, blank=True),
            ),
            (
                "created_at",
                models.DateTimeField(default=django.utils.timezone.now, editable=False),
            ),
            ("updated_at", models.DateTimeField(auto_now=True)),
            (
                "user",
                models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="providers",
                    to=settings.AUTH_USER_MODEL,
                ),
            ),
        ]
    )

    constraints = [
        migrations.AddConstraint(
            model_name="provider",
            constraint=models.UniqueConstraint(
                fields=["slug"] if not TENANCY_ENABLED else ["tenant", "slug"],
                name="providers_provider_slug_unique",
            ),
        ),
    ]
    indexes = [
        migrations.AddIndex(
            model_name="provider",
            index=models.Index(fields=["is_active", "visibility"], name="prov_active_vis_idx"),
        ),
    ]
    if TENANCY_ENABLED:
        indexes.append(
            migrations.AddIndex(
                model_name="provider",
                index=models.Index(
                    fields=["tenant", "is_active", "sort_order"],
                    name="prov_tenant_active_order_idx",
                ),
            )
        )

    operations.extend(constraints)
    operations.extend(indexes)

    provider_service_fields = [
        (
            "id",
            models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]
    if TENANCY_ENABLED:
        provider_service_fields.append(
            (
                "tenant",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="provider_services",
                    to=TENANT_MODEL,
                    db_index=True,
                ),
            )
        )
    provider_service_fields.extend(
        [
            ("is_active", models.BooleanField(default=True)),
            ("priority", models.IntegerField(default=0)),
            (
                "provider",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="provider_services",
                    to="providers.provider",
                ),
            ),
            (
                "service",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="provider_services",
                    to="services.service",
                ),
            ),
        ]
    )

    provider_service_indexes = [
        migrations.AddIndex(
            model_name="providerservice",
            index=models.Index(
                fields=["tenant", "priority"] if TENANCY_ENABLED else ["priority"],
                name="provsvc_tenant_priority_idx" if TENANCY_ENABLED else "provsvc_priority_idx",
            ),
        )
    ]

    operations.append(
        migrations.CreateModel(
            name="ProviderService",
            fields=provider_service_fields,
            options={
                "ordering": ["priority", "pk"],
            },
        )
    )
    operations.append(
        migrations.AddConstraint(
            model_name="providerservice",
            constraint=models.UniqueConstraint(
                fields=["provider", "service"],
                name="providers_providerservice_unique",
            ),
        )
    )
    operations.extend(provider_service_indexes)

    provider_image_fields = [
        (
            "id",
            models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]
    if TENANCY_ENABLED:
        provider_image_fields.append(
            (
                "tenant",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="provider_images",
                    to=TENANT_MODEL,
                    db_index=True,
                ),
            )
        )
    provider_image_fields.extend(
        [
            (
                "provider",
                models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="images",
                    to="providers.provider",
                ),
            ),
            ("image", models.ImageField(upload_to="providers/images/")),
            ("alt_text", models.CharField(blank=True, max_length=255)),
            ("sort_order", models.PositiveIntegerField(default=0)),
            (
                "created_at",
                models.DateTimeField(default=django.utils.timezone.now, editable=False),
            ),
        ]
    )
    operations.append(
        migrations.CreateModel(
            name="ProviderImage",
            fields=provider_image_fields,
            options={
                "ordering": ["sort_order", "pk"],
            },
        )
    )
    operations.append(
        migrations.AddIndex(
            model_name="providerimage",
            index=models.Index(
                fields=["sort_order"], name="provimg_sort_idx"
            ),
        )
    )
