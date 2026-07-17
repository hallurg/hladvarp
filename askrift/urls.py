from django.urls import path

from . import views


urlpatterns = [
    path("", views.askrift_hub, name="askrift_hub"),
    path("hladvarp/", views.hladvarp_storefront, name="askrift_hladvarp"),
    path("operator/", views.operator_redirect, name="askrift_operator"),
    path("operator/pricing/", views.pricing_redirect, name="askrift_pricing_admin"),
    path("operator/customer/<slug:slug>/", views.customer_detail, name="askrift_customer_detail"),
    path("operator/export.csv", views.export_csv, name="askrift_operator_export"),
    path("admin/", views.dashboard, name="askrift_admin_dashboard"),
    path("admin/products/", views.products, name="askrift_admin_products"),
    path("admin/storefronts/", views.storefronts, name="askrift_admin_storefronts"),
    path("admin/plans/", views.plans, name="askrift_admin_plans"),
    path("admin/organizations/", views.organizations, name="askrift_admin_organizations"),
    path("admin/customers/", views.customers, name="askrift_admin_customers"),
    path("admin/customers/<slug:slug>/", views.customer_detail, name="askrift_admin_customer_detail"),
    path("admin/subscriptions/", views.subscriptions, name="askrift_admin_subscriptions"),
    path("admin/invoices/", views.invoices, name="askrift_admin_invoices"),
    path("admin/payments/", views.payments, name="askrift_admin_payments"),
    path("admin/entitlements/", views.entitlements, name="askrift_admin_entitlements"),
    path("admin/roles/", views.roles, name="askrift_admin_roles"),
    path("admin/overrides/", views.overrides, name="askrift_admin_overrides"),
    path("admin/notes/", views.notes, name="askrift_admin_notes"),
    path("admin/integrations/", views.integrations, name="askrift_admin_integrations"),
    path("admin/preview/<slug:tenant_key>/", views.storefront_preview, name="askrift_admin_storefront_preview"),
    path("admin/storefronts/<int:pk>/status/<slug:status>/", views.set_storefront_status, name="askrift_admin_storefront_status"),
    path("admin/plans/<int:pk>/status/<slug:status>/", views.set_plan_status, name="askrift_admin_plan_status"),
    path("admin/export.csv", views.export_csv, name="askrift_admin_export"),
]
