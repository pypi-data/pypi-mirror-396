from django.contrib import admin

from providers import conf
from providers.models import Provider, ProviderImage, ProviderService

TENANT_ENABLED = conf.tenant_enabled()


class ProviderServiceInline(admin.TabularInline):
    model = ProviderService
    extra = 0
    fields = ("service", "is_active", "priority")
    raw_id_fields = ("service",)


class ProviderImageInline(admin.TabularInline):
    model = ProviderImage
    extra = 0
    fields = ("image", "alt_text", "sort_order")


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    inlines = [ProviderServiceInline, ProviderImageInline]
    list_display = (
        "name",
        "provider_type",
        "is_active",
        "visibility",
        "sort_order",
    ) + (("tenant",) if TENANT_ENABLED else ())
    list_filter = ("provider_type", "is_active", "visibility") + (
        ("tenant",) if TENANT_ENABLED else ()
    )
    search_fields = ("name", "slug")
    ordering = ("sort_order", "name")
    raw_id_fields = ("user",) + (("tenant",) if TENANT_ENABLED else ())

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if TENANT_ENABLED and hasattr(instance, "tenant_id") and not instance.tenant_id:
                instance.tenant = form.instance.tenant
            instance.full_clean()
            instance.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()


@admin.register(ProviderService)
class ProviderServiceAdmin(admin.ModelAdmin):
    list_display = ("provider", "service", "is_active", "priority") + (
        ("tenant",) if TENANT_ENABLED else ()
    )
    list_filter = ("is_active",) + (("tenant",) if TENANT_ENABLED else ())
    raw_id_fields = ("provider", "service") + (("tenant",) if TENANT_ENABLED else ())
    ordering = ("priority", "provider")

    def save_model(self, request, obj, form, change):
        if TENANT_ENABLED and hasattr(obj, "tenant_id") and not obj.tenant_id:
            obj.tenant = obj.provider.tenant
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(ProviderImage)
class ProviderImageAdmin(admin.ModelAdmin):
    list_display = ("provider", "sort_order") + (("tenant",) if TENANT_ENABLED else ())
    raw_id_fields = ("provider",) + (("tenant",) if TENANT_ENABLED else ())
    ordering = ("sort_order", "provider")

    def save_model(self, request, obj, form, change):
        if TENANT_ENABLED and hasattr(obj, "tenant_id") and not obj.tenant_id:
            obj.tenant = obj.provider.tenant
        obj.full_clean()
        super().save_model(request, obj, form, change)
