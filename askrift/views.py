import csv

from django.contrib import messages
from django.db.models import Count, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import (
    AccountNoteForm,
    AdminOverrideForm,
    AdminRoleForm,
    CustomerForm,
    EntitlementRuleForm,
    IntegrationStatusForm,
    InvoiceForm,
    ManualSignupForm,
    OrganizationForm,
    PaymentRecordForm,
    PlanForm,
    ProductForm,
    StorefrontForm,
    SubscriptionForm,
)
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
from .services import create_manual_signup, ensure_default_account_data


ADMIN_SECTIONS = [
    ("Yfirlit", "askrift_admin_dashboard"),
    ("Vörur", "askrift_admin_products"),
    ("Storefront", "askrift_admin_storefronts"),
    ("Verð", "askrift_admin_plans"),
    ("Viðskiptavinir", "askrift_admin_customers"),
    ("Áskriftir", "askrift_admin_subscriptions"),
    ("Reikningar", "askrift_admin_invoices"),
    ("Entitlements", "askrift_admin_entitlements"),
    ("Hlutverk", "askrift_admin_roles"),
    ("Kerfistengingar", "askrift_admin_integrations"),
]


def admin_context(active):
    return {"admin_sections": ADMIN_SECTIONS, "active_admin_section": active}


def askrift_hub(request):
    product, storefront = ensure_default_account_data()
    return render(request, "askrift/hub.html", {"product": product, "storefront": storefront})


@require_http_methods(["GET", "POST"])
def hladvarp_storefront(request):
    product, storefront = ensure_default_account_data()
    signup_result = None
    form = ManualSignupForm(request.POST or None, product=product)
    if request.method == "POST" and form.is_valid():
        customer, subscription = create_manual_signup(form.cleaned_data)
        signup_result = {"customer": customer, "subscription": subscription}
        form = ManualSignupForm(product=product)
    plans = product.plans.exclude(status=Plan.Status.RETIRED).order_by("sort_order")
    return render(
        request,
        "askrift/hladvarp.html",
        {
            "product": product,
            "storefront": storefront,
            "plans": plans,
            "form": form,
            "signup_result": signup_result,
        },
    )


def dashboard(request):
    ensure_default_account_data()
    subscriptions = Subscription.objects.select_related("customer", "plan", "product")
    paid = subscriptions.filter(status=Subscription.Status.PAID)
    review = subscriptions.filter(status__in=[Subscription.Status.MANUAL_PENDING, Subscription.Status.UNPAID, Subscription.Status.TRIAL])
    invoices = Invoice.objects.all()
    unpaid = subscriptions.filter(status=Subscription.Status.UNPAID)
    gross_revenue = paid.aggregate(total=Sum("plan__gross_price"))["total"] or 0
    vat_estimate = sum((subscription.plan.vat_amount for subscription in paid), 0)
    context = {
        "products": Product.objects.all(),
        "storefronts": Storefront.objects.select_related("product"),
        "subscriptions": subscriptions[:8],
        "review_subscriptions": review[:8],
        "unpaid_subscriptions": unpaid[:8],
        "entitlements": EntitlementRule.objects.select_related("product"),
        "integrations": IntegrationStatus.objects.select_related("product"),
        "roles": AdminRole.objects.all(),
        "audit_events": AuditEvent.objects.all()[:8],
        "stats": {
            "products": Product.objects.count(),
            "customers": Customer.objects.count(),
            "active_subscriptions": subscriptions.exclude(status__in=[Subscription.Status.CANCELLED, Subscription.Status.PAUSED]).count(),
            "needs_review": review.count(),
            "paid": paid.count(),
            "unpaid": unpaid.count(),
            "gross_revenue": gross_revenue,
            "vat_estimate": vat_estimate,
            "invoice_drafts": invoices.filter(status=Invoice.Status.DRAFT).count(),
        },
    }
    context.update(admin_context("Yfirlit"))
    return render(request, "askrift/admin/dashboard.html", context)


def model_admin(request, label, model, form_class, template="askrift/admin/list_edit.html", queryset=None):
    ensure_default_account_data()
    instance = None
    if request.GET.get("edit"):
        instance = get_object_or_404(model, pk=request.GET["edit"])
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        AuditEvent.objects.create(
            actor=request.POST.get("actor", "admin"),
            action=f"{model.__name__.lower()}_saved",
            target=str(saved),
            summary=f"{label} vistað í account admin.",
        )
        messages.success(request, f"{label} vistað.")
        return redirect(request.path)
    rows = queryset if queryset is not None else model.objects.all()
    context = {
        "label": label,
        "rows": rows,
        "form": form,
        "editing": instance,
        "model_name": model.__name__,
    }
    context.update(admin_context(label))
    return render(request, template, context)


def products(request):
    return model_admin(request, "Vörur", Product, ProductForm, queryset=Product.objects.all())


def storefronts(request):
    return model_admin(request, "Storefront", Storefront, StorefrontForm, queryset=Storefront.objects.select_related("product"))


def plans(request):
    return model_admin(request, "Verð", Plan, PlanForm, queryset=Plan.objects.select_related("product"))


def organizations(request):
    return model_admin(request, "Fyrirtæki", Organization, OrganizationForm)


def customers(request):
    return model_admin(request, "Viðskiptavinir", Customer, CustomerForm, queryset=Customer.objects.select_related("organization"))


def subscriptions(request):
    return model_admin(request, "Áskriftir", Subscription, SubscriptionForm, queryset=Subscription.objects.select_related("customer", "product", "plan"))


def invoices(request):
    return model_admin(request, "Reikningar", Invoice, InvoiceForm, queryset=Invoice.objects.select_related("subscription", "subscription__customer"))


def payments(request):
    return model_admin(request, "Greiðslusaga", PaymentRecord, PaymentRecordForm, queryset=PaymentRecord.objects.select_related("subscription", "subscription__customer"))


def entitlements(request):
    return model_admin(request, "Entitlements", EntitlementRule, EntitlementRuleForm, queryset=EntitlementRule.objects.select_related("product"))


def overrides(request):
    return model_admin(request, "Overrides", AdminOverride, AdminOverrideForm, queryset=AdminOverride.objects.select_related("customer", "subscription"))


def notes(request):
    return model_admin(request, "Minnispunktar", AccountNote, AccountNoteForm, queryset=AccountNote.objects.select_related("customer"))


def integrations(request):
    return model_admin(request, "Kerfistengingar", IntegrationStatus, IntegrationStatusForm, queryset=IntegrationStatus.objects.select_related("product"))


def roles(request):
    return model_admin(request, "Hlutverk", AdminRole, AdminRoleForm)


@require_POST
def set_storefront_status(request, pk, status):
    ensure_default_account_data()
    if status not in {Storefront.Status.LIVE, Storefront.Status.PAUSED, Storefront.Status.DRAFT}:
        raise Http404
    storefront = get_object_or_404(Storefront.objects.select_related("product"), pk=pk)
    storefront.status = status
    if status == Storefront.Status.LIVE and storefront.published_at is None:
        storefront.published_at = timezone.now()
    storefront.save(update_fields=["status", "published_at", "updated_at"])
    AuditEvent.objects.create(
        actor=request.POST.get("actor", "CEO/admin"),
        action="storefront_status_changed",
        target=str(storefront),
        summary=f"Storefront status changed to {storefront.get_status_display()} from account admin.",
    )
    messages.success(request, f"Storefront sett í stöðu: {storefront.get_status_display()}.")
    return redirect("askrift_admin_storefronts")


@require_POST
def set_plan_status(request, pk, status):
    ensure_default_account_data()
    if status not in {Plan.Status.LIVE, Plan.Status.HIDDEN, Plan.Status.DRAFT, Plan.Status.RETIRED}:
        raise Http404
    plan = get_object_or_404(Plan.objects.select_related("product"), pk=pk)
    plan.status = status
    plan.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(
        actor=request.POST.get("actor", "CEO/admin"),
        action="plan_status_changed",
        target=str(plan),
        summary=f"Plan status changed to {plan.get_status_display()} from account admin.",
    )
    messages.success(request, f"Verðleið sett í stöðu: {plan.get_status_display()}.")
    return redirect("askrift_admin_plans")


def customer_detail(request, slug):
    customer = get_object_or_404(Customer.objects.select_related("organization"), slug=slug)
    context = {
        "customer": customer,
        "subscriptions": customer.subscriptions.select_related("product", "plan"),
        "notes": customer.notes.all(),
        "overrides": customer.overrides.all(),
    }
    context.update(admin_context("Viðskiptavinir"))
    return render(request, "askrift/admin/customer_detail.html", context)


def storefront_preview(request, tenant_key="hladvarp"):
    ensure_default_account_data()
    storefront = get_object_or_404(Storefront.objects.select_related("product"), tenant_key=tenant_key)
    plans = storefront.product.plans.exclude(status=Plan.Status.RETIRED).order_by("sort_order")
    return render(
        request,
        "askrift/hladvarp.html",
        {
            "product": storefront.product,
            "storefront": storefront,
            "plans": plans,
            "form": ManualSignupForm(product=storefront.product),
            "signup_result": None,
            "is_preview": True,
        },
    )


def operator_redirect(request):
    return redirect("askrift_admin_dashboard")


def pricing_redirect(request):
    return redirect("askrift_admin_plans")


def export_csv(request):
    ensure_default_account_data()
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="account-subscriptions.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "customer",
        "email",
        "organization",
        "product",
        "plan",
        "status",
        "advertising_visible",
        "gross_price",
        "net_price",
        "vat_amount",
        "next_billing_date",
        "operator_note",
    ])
    for subscription in Subscription.objects.select_related("customer", "customer__organization", "product", "plan"):
        writer.writerow([
            subscription.customer.name,
            subscription.customer.email,
            subscription.customer.organization.name if subscription.customer.organization else "",
            subscription.product.public_name,
            subscription.plan.name,
            subscription.status,
            "yes" if subscription.advertising_visible else "no",
            subscription.plan.gross_price,
            subscription.plan.net_price,
            subscription.plan.vat_amount,
            subscription.next_billing_date or "",
            subscription.operator_note,
        ])
    return response
