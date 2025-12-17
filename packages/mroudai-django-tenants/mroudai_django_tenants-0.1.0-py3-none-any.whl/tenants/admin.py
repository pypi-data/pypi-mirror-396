from django.contrib import admin

from .models import Tenant, TenantDomain, TenantMembership


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 0
    raw_id_fields = ("user",)


class TenantDomainInline(admin.TabularInline):
    model = TenantDomain
    extra = 0
    show_change_link = True


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "timezone", "currency", "created_at")
    search_fields = ("name", "slug", "contact_email")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (TenantMembershipInline, TenantDomainInline)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("tenant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("tenant__name", "user__username", "user__email")
    raw_id_fields = ("tenant", "user")
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary", "created_at")
    list_filter = ("is_primary",)
    search_fields = ("domain", "tenant__name")
    raw_id_fields = ("tenant",)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)
