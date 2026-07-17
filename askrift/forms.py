import re

from django import forms
from django.utils.text import slugify

from .models import (
    AccountNote,
    AdminOverride,
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
    AdminRole,
)


class KnModelForm(forms.ModelForm):
    required_css_class = "required"


class ProductForm(KnModelForm):
    class Meta:
        model = Product
        fields = ["name", "slug", "public_name", "description", "status", "public_domain", "account_route", "handoff_note"]


class StorefrontForm(KnModelForm):
    class Meta:
        model = Storefront
        fields = [
            "product",
            "tenant_key",
            "status",
            "headline",
            "subheadline",
            "intro_text",
            "brand_note",
            "primary_cta",
            "secondary_cta",
            "support_email",
            "brand_primary_color",
            "brand_accent_color",
            "brand_background_color",
            "brand_surface_color",
            "brand_text_color",
            "typography_note",
            "hero_image_url",
            "preview_note",
        ]
        widgets = {
            "subheadline": forms.Textarea(attrs={"rows": 3}),
            "intro_text": forms.Textarea(attrs={"rows": 4}),
            "preview_note": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field in [
            "brand_primary_color",
            "brand_accent_color",
            "brand_background_color",
            "brand_surface_color",
            "brand_text_color",
        ]:
            value = cleaned_data.get(field)
            if value and not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
                self.add_error(field, "Notaðu sex stafa HEX lit, t.d. #f0b64d.")
        return cleaned_data


class PlanForm(KnModelForm):
    class Meta:
        model = Plan
        fields = [
            "product",
            "slug",
            "name",
            "public_description",
            "billing_interval",
            "gross_price",
            "vat_rate",
            "effective_from",
            "effective_to",
            "status",
            "public_cta",
            "sort_order",
            "advertising_allowed_when_paid",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
            "public_description": forms.Textarea(attrs={"rows": 3}),
        }


class OrganizationForm(KnModelForm):
    class Meta:
        model = Organization
        fields = ["name", "kennitala", "billing_email", "accounting_reference", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}


class CustomerForm(KnModelForm):
    class Meta:
        model = Customer
        fields = ["organization", "name", "slug", "email", "phone", "product_label", "status", "internal_flag", "support_summary"]
        widgets = {"support_summary": forms.Textarea(attrs={"rows": 3})}


class SubscriptionForm(KnModelForm):
    class Meta:
        model = Subscription
        fields = [
            "customer",
            "product",
            "plan",
            "status",
            "starts_at",
            "ends_at",
            "trial_ends_at",
            "paid_at",
            "paused_at",
            "cancelled_at",
            "next_billing_date",
            "operator_note",
        ]
        widgets = {
            "starts_at": forms.DateInput(attrs={"type": "date"}),
            "ends_at": forms.DateInput(attrs={"type": "date"}),
            "trial_ends_at": forms.DateInput(attrs={"type": "date"}),
            "paid_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "paused_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "cancelled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "next_billing_date": forms.DateInput(attrs={"type": "date"}),
            "operator_note": forms.Textarea(attrs={"rows": 3}),
        }


class PaymentRecordForm(KnModelForm):
    class Meta:
        model = PaymentRecord
        fields = ["subscription", "amount", "currency", "status", "method", "reference", "received_at", "recorded_by", "note"]
        widgets = {
            "received_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }


class InvoiceForm(KnModelForm):
    class Meta:
        model = Invoice
        fields = [
            "subscription",
            "invoice_number",
            "status",
            "period_start",
            "period_end",
            "net_amount",
            "vat_amount",
            "gross_amount",
            "accounting_code",
            "export_reference",
            "note",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }


class EntitlementRuleForm(KnModelForm):
    class Meta:
        model = EntitlementRule
        fields = ["product", "code", "name", "description", "downstream_system", "requires_paid_subscription", "is_live"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class AdminOverrideForm(KnModelForm):
    class Meta:
        model = AdminOverride
        fields = ["customer", "subscription", "state", "reason", "created_by", "expires_at"]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class AccountNoteForm(KnModelForm):
    class Meta:
        model = AccountNote
        fields = ["customer", "note", "flag", "created_by"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3})}


class IntegrationStatusForm(KnModelForm):
    class Meta:
        model = IntegrationStatus
        fields = ["product", "system_name", "state", "public_route", "safe_summary", "last_checked_at"]
        widgets = {
            "safe_summary": forms.Textarea(attrs={"rows": 3}),
            "last_checked_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class AdminRoleForm(KnModelForm):
    class Meta:
        model = AdminRole
        fields = [
            "name",
            "slug",
            "description",
            "can_manage_catalog",
            "can_manage_customers",
            "can_manage_billing",
            "can_manage_entitlements",
            "can_publish_storefront",
            "can_manage_integrations",
            "can_view_revenue",
            "is_active",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ManualSignupForm(forms.Form):
    name = forms.CharField(label="Nafn tengiliðar", max_length=160)
    email = forms.EmailField(label="Netfang")
    organization = forms.CharField(label="Fyrirtæki eða aðili", max_length=160, required=False)
    podcast = forms.CharField(label="Nafn hlaðvarps", max_length=160)
    plan = forms.ModelChoiceField(label="Áskriftarleið", queryset=Plan.objects.none())
    monetization = forms.ChoiceField(
        label="Tegund tekjuöflunar",
        choices=[
            ("none", "Engin tekjuöflun"),
            ("sponsorship", "Kostun"),
            ("ads", "Auglýsingar"),
            ("paid_promo", "Greidd kynning"),
            ("subscription", "Áskriftartekjur"),
            ("unsure", "Óvíst / þarf samtal"),
        ],
    )
    notes = forms.CharField(label="Athugasemdir", required=False, widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        if product:
            self.fields["plan"].queryset = product.plans.exclude(status=Plan.Status.RETIRED).order_by("sort_order")

    def clean_podcast(self):
        value = self.cleaned_data["podcast"].strip()
        if not slugify(value, allow_unicode=True):
            raise forms.ValidationError("Nafn hlaðvarps þarf að innihalda bókstafi eða tölustafi.")
        return value
