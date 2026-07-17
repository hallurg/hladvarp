from django.contrib import admin

from .models import (
    AccountNote,
    AdminOverride,
    AdminRole,
    AuditEvent,
    Customer,
    EntitlementRule,
    IntegrationStatus,
    Invoice,
    Organization,
    PaymentRecord,
    Plan,
    Product,
    Storefront,
    Subscription,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("public_name", "slug", "status", "public_domain", "account_route")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Storefront)
class StorefrontAdmin(admin.ModelAdmin):
    list_display = ("product", "tenant_key", "status", "brand_primary_color", "brand_accent_color", "published_at")
    list_filter = ("status", "product")


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "status", "billing_interval", "gross_price", "net_price", "vat_rate", "advertising_allowed_when_paid")
    list_filter = ("status", "billing_interval", "product", "advertising_allowed_when_paid")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "organization", "status", "internal_flag")
    list_filter = ("status",)
    search_fields = ("name", "email", "organization__name", "product_label")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Organization)
admin.site.register(AdminRole)
admin.site.register(Subscription)
admin.site.register(PaymentRecord)
admin.site.register(Invoice)
admin.site.register(EntitlementRule)
admin.site.register(AdminOverride)
admin.site.register(AccountNote)
admin.site.register(IntegrationStatus)
admin.site.register(AuditEvent)
