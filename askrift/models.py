from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Drög"
        LIVE = "live", "Í birtingu"
        PAUSED = "paused", "Í bið"

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    public_name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    public_domain = models.CharField(max_length=180, blank=True)
    account_route = models.CharField(max_length=180, default="/askrift/")
    handoff_note = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.public_name


class Storefront(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Drög"
        LIVE = "live", "Í birtingu"
        PAUSED = "paused", "Í bið"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="storefronts")
    tenant_key = models.SlugField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    headline = models.CharField(max_length=180)
    subheadline = models.TextField()
    intro_text = models.TextField(blank=True)
    brand_note = models.CharField(max_length=180, blank=True)
    primary_cta = models.CharField(max_length=80, default="Senda beiðni")
    secondary_cta = models.CharField(max_length=80, default="Skoða leiðir")
    support_email = models.EmailField(blank=True)
    brand_primary_color = models.CharField(max_length=20, default="#f0b64d")
    brand_accent_color = models.CharField(max_length=20, default="#67c7ba")
    brand_background_color = models.CharField(max_length=20, default="#10100d")
    brand_surface_color = models.CharField(max_length=20, default="#242017")
    brand_text_color = models.CharField(max_length=20, default="#fff8e8")
    typography_note = models.CharField(max_length=180, blank=True)
    hero_image_url = models.URLField(blank=True)
    preview_note = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("product", "tenant_key")]
        ordering = ["product__name", "tenant_key"]

    def __str__(self):
        return f"{self.product.public_name} / {self.tenant_key}"

    @property
    def is_live(self):
        return self.status == self.Status.LIVE


class AdminRole(TimestampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    can_manage_catalog = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_manage_entitlements = models.BooleanField(default=False)
    can_publish_storefront = models.BooleanField(default=False)
    can_manage_integrations = models.BooleanField(default=False)
    can_view_revenue = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Plan(TimestampedModel):
    class Interval(models.TextChoices):
        NONE = "none", "Engin gjaldfærsla"
        MONTHLY = "monthly", "Mánaðarlega"
        YEARLY = "yearly", "Árlega"
        MANUAL = "manual", "Handvirkt mat"

    class Status(models.TextChoices):
        DRAFT = "draft", "Drög"
        LIVE = "live", "Í birtingu"
        HIDDEN = "hidden", "Falið"
        RETIRED = "retired", "Aflagt"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="plans")
    slug = models.SlugField()
    name = models.CharField(max_length=140)
    public_description = models.TextField()
    billing_interval = models.CharField(max_length=20, choices=Interval.choices, default=Interval.MONTHLY)
    gross_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.2400"))
    effective_from = models.DateField(default=timezone.localdate)
    effective_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    public_cta = models.CharField(max_length=80, default="Senda beiðni")
    sort_order = models.PositiveIntegerField(default=100)
    advertising_allowed_when_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = [("product", "slug")]
        ordering = ["product__name", "sort_order", "name"]

    def __str__(self):
        return f"{self.product.public_name}: {self.name}"

    def save(self, *args, **kwargs):
        if self.gross_price is not None and self.vat_rate is not None:
            divisor = Decimal("1") + self.vat_rate
            self.net_price = (self.gross_price / divisor).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    @property
    def vat_amount(self):
        return (self.gross_price - self.net_price).quantize(Decimal("1.00"))

    @property
    def is_live(self):
        today = timezone.localdate()
        return (
            self.status == self.Status.LIVE
            and self.effective_from <= today
            and (self.effective_to is None or self.effective_to >= today)
        )


class Organization(TimestampedModel):
    name = models.CharField(max_length=160)
    kennitala = models.CharField(max_length=20, blank=True)
    billing_email = models.EmailField(blank=True)
    accounting_reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(TimestampedModel):
    class Status(models.TextChoices):
        LEAD = "lead", "Nýr tengiliður"
        ACTIVE = "active", "Virkur"
        REVIEW = "review", "Þarf yfirferð"
        PAUSED = "paused", "Í bið"
        CLOSED = "closed", "Lokað"

    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="customers")
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=60, blank=True)
    product_label = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD)
    internal_flag = models.CharField(max_length=140, blank=True)
    support_summary = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("askrift_admin_customer_detail", kwargs={"slug": self.slug})


class Subscription(TimestampedModel):
    class Status(models.TextChoices):
        TRIAL = "trial", "Prufa"
        MANUAL_PENDING = "manual_pending", "Handvirkt í bið"
        MANUAL_ACTIVE = "manual_active", "Handvirkt virkt"
        PAID = "paid", "Greitt"
        UNPAID = "unpaid", "Ógreitt"
        PAUSED = "paused", "Í bið"
        CANCELLED = "cancelled", "Hætt"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="subscriptions")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.MANUAL_PENDING)
    starts_at = models.DateField(default=timezone.localdate)
    ends_at = models.DateField(null=True, blank=True)
    trial_ends_at = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    operator_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer} / {self.plan}"

    @property
    def is_paid_for_entitlements(self):
        today = timezone.localdate()
        if self.status != self.Status.PAID:
            return False
        if self.ends_at and self.ends_at < today:
            return False
        return True

    @property
    def advertising_visible(self):
        return self.is_paid_for_entitlements and self.plan.advertising_allowed_when_paid


class PaymentRecord(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Drög"
        RECORDED = "recorded", "Skráð"
        VOID = "void", "Ógilt"

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="ISK")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECORDED)
    method = models.CharField(max_length=80, default="Handvirkt")
    reference = models.CharField(max_length=160, blank=True)
    received_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-received_at"]


class Invoice(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Drög"
        ISSUED = "issued", "Útgefið"
        PAID = "paid", "Greitt"
        CANCELLED = "cancelled", "Fellt niður"

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accounting_code = models.CharField(max_length=80, blank=True)
    export_reference = models.CharField(max_length=160, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class EntitlementRule(TimestampedModel):
    class Downstream(models.TextChoices):
        HLADVARP = "hladvarp", "KN/Hlaðvarp"
        CAYENNEPOD = "cayennepod", "CayennePod"
        BOTH = "both", "Bæði"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="entitlement_rules")
    code = models.SlugField()
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    downstream_system = models.CharField(max_length=30, choices=Downstream.choices, default=Downstream.BOTH)
    requires_paid_subscription = models.BooleanField(default=True)
    is_live = models.BooleanField(default=False)

    class Meta:
        unique_together = [("product", "code")]
        ordering = ["product__name", "code"]


class AdminOverride(TimestampedModel):
    class State(models.TextChoices):
        NOTE = "note", "Athugasemd"
        TEMPORARY_ALLOW = "temporary_allow", "Tímabundin undanþága"
        TEMPORARY_BLOCK = "temporary_block", "Tímabundin lokun"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="overrides")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True, related_name="overrides")
    state = models.CharField(max_length=40, choices=State.choices, default=State.NOTE)
    reason = models.TextField()
    created_by = models.CharField(max_length=120, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class AccountNote(TimestampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()
    flag = models.CharField(max_length=120, blank=True)
    created_by = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]


class IntegrationStatus(TimestampedModel):
    class State(models.TextChoices):
        OFF = "off", "Óvirkt"
        READY = "ready", "Tilbúið"
        NEEDS_APPROVAL = "needs_approval", "Þarf samþykki"
        BLOCKED = "blocked", "Stoppað"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="integrations")
    system_name = models.CharField(max_length=120)
    state = models.CharField(max_length=30, choices=State.choices, default=State.OFF)
    public_route = models.CharField(max_length=180, blank=True)
    safe_summary = models.TextField(blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["product__name", "system_name"]


class AuditEvent(TimestampedModel):
    actor = models.CharField(max_length=120, blank=True)
    action = models.CharField(max_length=140)
    target = models.CharField(max_length=180, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
