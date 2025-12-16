from django.contrib import admin

from . import conf
from .models import Service, ServiceAddon, ServiceCategory


class ServiceAddonInline(admin.TabularInline):
    model = ServiceAddon
    extra = 0
    fields = ("name", "slug", "pricing_type", "price_amount", "is_active", "sort_order")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        return super().save_model(request, obj, form, change)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order") + (
        ("tenant",) if conf.tenant_model() else ()
    )
    search_fields = ("name", "slug")
    ordering = ("sort_order", "name")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        return super().save_model(request, obj, form, change)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "duration_minutes",
        "price_amount",
        "is_active",
        "visibility",
        "sort_order",
    ) + (("tenant",) if conf.tenant_model() else ())
    list_filter = ("is_active", "visibility", "pricing_type", "category") + (
        ("tenant",) if conf.tenant_model() else ()
    )
    search_fields = ("name", "slug")
    inlines = [ServiceAddonInline]

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        return super().save_model(request, obj, form, change)


@admin.register(ServiceAddon)
class ServiceAddonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service",
        "pricing_type",
        "price_amount",
        "is_active",
        "sort_order",
    ) + (("tenant",) if conf.tenant_model() else ())
    list_filter = ("is_active", "pricing_type") + (
        ("tenant",) if conf.tenant_model() else ()
    )
    search_fields = ("name", "slug", "service__name")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        return super().save_model(request, obj, form, change)
