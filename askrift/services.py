from decimal import Decimal

from django.utils import timezone
from django.utils.text import slugify

from .models import (
    AdminRole,
    AuditEvent,
    Customer,
    EntitlementRule,
    IntegrationStatus,
    Organization,
    Plan,
    Product,
    Storefront,
    Subscription,
)


def unique_slug(model, value, field="slug"):
    base = slugify(value, allow_unicode=True) or "item"
    slug = base
    counter = 2
    while model.objects.filter(**{field: slug}).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def ensure_default_account_data():
    product, _ = Product.objects.get_or_create(
        slug="hladvarp",
        defaults={
            "name": "Hlaðvarp",
            "public_name": "Hlaðvarp.com",
            "description": "Sjálfstæð hlaðvarpsveita með handvirku áskriftarferli fyrir tekjuöflun.",
            "status": Product.Status.LIVE,
            "public_domain": "hladvarp.com",
            "account_route": "/askrift/hladvarp/",
            "handoff_note": "Customer-facing flow á að líta út eins og Hlaðvarp, þó reikningshluti sé á account.kaupfjelag.com.",
        },
    )

    storefront, _ = Storefront.objects.get_or_create(
        product=product,
        tenant_key="hladvarp",
        defaults={
            "status": Storefront.Status.LIVE,
            "headline": "Áskrift fyrir hlaðvörp sem afla tekna",
            "subheadline": "Hlaðvarp má vera ókeypis fyrir samfélag og áhuga. Þegar kostun, auglýsingar eða greidd kynning koma inn fer það í skýrt handvirkt áskriftarferli.",
            "intro_text": "Engin greiðslusöfnun er virk hér. Þú sendir beiðni, operator fer yfir stöðuna og staðfestir næstu skref.",
            "brand_note": "Kaffispjall og aðrar vangaveltur",
            "primary_cta": "Senda beiðni",
            "secondary_cta": "Skoða leiðir",
            "support_email": "askrift@kaupfjelag.com",
            "brand_primary_color": "#f0b64d",
            "brand_accent_color": "#67c7ba",
            "brand_background_color": "#10100d",
            "brand_surface_color": "#242017",
            "brand_text_color": "#fff8e8",
            "typography_note": "Match Hlaðvarp.com: dark listening-room surface, warm gold actions, compact podcast controls.",
            "preview_note": "Preview must feel like Hlaðvarp before publishing; account mechanics stay behind the branded storefront.",
            "published_at": timezone.now(),
        },
    )
    storefront_updates = {}
    if not storefront.typography_note:
        storefront_updates["typography_note"] = "Match Hlaðvarp.com: dark listening-room surface, warm gold actions, compact podcast controls."
    if not storefront.preview_note:
        storefront_updates["preview_note"] = "Preview must feel like Hlaðvarp before publishing; account mechanics stay behind the branded storefront."
    if storefront_updates:
        for field, value in storefront_updates.items():
            setattr(storefront, field, value)
        storefront.save(update_fields=[*storefront_updates.keys(), "updated_at"])

    defaults = [
        {
            "slug": "okeypis",
            "name": "Ókeypis hlaðvarp",
            "public_description": "Fyrir hlaðvörp án auglýsinga, kostunar, greiddrar kynningar eða áskriftartekna.",
            "billing_interval": Plan.Interval.NONE,
            "gross_price": Decimal("0"),
            "status": Plan.Status.LIVE,
            "public_cta": "Halda áfram ókeypis",
            "sort_order": 10,
            "advertising_allowed_when_paid": False,
        },
        {
            "slug": "tekjuoflun",
            "name": "Tekjuöflun",
            "public_description": "Fyrir kostun, auglýsingar, greidda kynningu eða sambærilega tekjuöflun.",
            "billing_interval": Plan.Interval.MONTHLY,
            "gross_price": Decimal("12400"),
            "status": Plan.Status.LIVE,
            "public_cta": "Senda handvirka beiðni",
            "sort_order": 20,
            "advertising_allowed_when_paid": True,
        },
        {
            "slug": "fyrirtaeki-stofnun",
            "name": "Fyrirtæki / stofnun",
            "public_description": "Sérmat fyrir rekstrar- eða vörumerkjahlaðvörp.",
            "billing_interval": Plan.Interval.MANUAL,
            "gross_price": Decimal("0"),
            "status": Plan.Status.DRAFT,
            "public_cta": "Bóka samtal",
            "sort_order": 30,
            "advertising_allowed_when_paid": True,
        },
    ]
    for row in defaults:
        Plan.objects.get_or_create(product=product, slug=row["slug"], defaults=row)

    EntitlementRule.objects.get_or_create(
        product=product,
        code="advertising",
        defaults={
            "name": "Auglýsingar og tekjuöflun",
            "description": "Auglýsingakerfi má aðeins sjást og virkjast fyrir greidda áskrift.",
            "downstream_system": EntitlementRule.Downstream.BOTH,
            "requires_paid_subscription": True,
            "is_live": False,
        },
    )

    for system_name, route in [
        ("KN/Hlaðvarp", "https://hladvarp.com/"),
        ("CayennePod", ""),
        ("account.kaupfjelag.com", "https://account.kaupfjelag.com/askrift/hladvarp/"),
    ]:
        IntegrationStatus.objects.get_or_create(
            product=product,
            system_name=system_name,
            defaults={
                "state": IntegrationStatus.State.NEEDS_APPROVAL if system_name != "account.kaupfjelag.com" else IntegrationStatus.State.READY,
                "public_route": route,
                "safe_summary": "Staða án leyndarmála. Engin provider token, OAuth eða webhook virk.",
            },
        )

    AdminRole.objects.get_or_create(
        slug="ceo-platform-owner",
        defaults={
            "name": "CEO / Product Owner",
            "description": "Full non-developer account control. Can publish storefront/admin configuration, manage billing records, and review safe integration status.",
            "can_manage_catalog": True,
            "can_manage_customers": True,
            "can_manage_billing": True,
            "can_manage_entitlements": True,
            "can_publish_storefront": True,
            "can_manage_integrations": True,
            "can_view_revenue": True,
        },
    )
    AdminRole.objects.get_or_create(
        slug="billing-operator",
        defaults={
            "name": "Billing operator",
            "description": "Can manage customers, subscriptions, manual payment records, invoice drafts, notes, and support flags. Cannot publish storefronts.",
            "can_manage_customers": True,
            "can_manage_billing": True,
            "can_view_revenue": True,
        },
    )
    AdminRole.objects.get_or_create(
        slug="integration-reviewer",
        defaults={
            "name": "Integration reviewer",
            "description": "Can review downstream integration status and entitlement configuration without seeing secrets or changing live billing.",
            "can_manage_entitlements": True,
            "can_manage_integrations": True,
        },
    )

    return product, storefront


def create_manual_signup(cleaned_data):
    product = cleaned_data["plan"].product
    organization = None
    if cleaned_data.get("organization"):
        organization, _ = Organization.objects.get_or_create(name=cleaned_data["organization"].strip())

    customer = Customer.objects.create(
        organization=organization,
        name=cleaned_data["name"],
        slug=unique_slug(Customer, cleaned_data["podcast"]),
        email=cleaned_data["email"],
        product_label=cleaned_data["podcast"],
        status=Customer.Status.REVIEW,
        internal_flag="Ný handvirk áskriftarbeiðni",
        support_summary=cleaned_data.get("notes", ""),
    )
    subscription = Subscription.objects.create(
        customer=customer,
        product=product,
        plan=cleaned_data["plan"],
        status=Subscription.Status.MANUAL_PENDING,
        operator_note=f"Tekjuöflun: {cleaned_data['monetization']}. {cleaned_data.get('notes', '')}".strip(),
    )
    AuditEvent.objects.create(
        actor=cleaned_data["email"],
        action="manual_signup_created",
        target=f"{customer.name} / {subscription.plan.name}",
        summary="Customer-facing manual signup created a review record. No payment was collected.",
    )
    return customer, subscription
