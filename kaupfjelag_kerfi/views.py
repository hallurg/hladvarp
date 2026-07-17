import csv
from decimal import Decimal, ROUND_HALF_UP

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


VAT_RATE = Decimal("0.24")


def money(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def vat_breakdown(gross_amount, vat_rate=VAT_RATE):
    gross = Decimal(gross_amount)
    net = (gross / (Decimal("1") + vat_rate)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    vat = gross - net
    return {
        "gross": money(gross),
        "net": money(net),
        "vat": money(vat),
        "vat_rate": int(vat_rate * 100),
    }


SUBSCRIPTION_PLANS = [
    {
        "name": "Okeypis hlaðvarp",
        "label": "Fyrir áhugamál og samfélag",
        "price": "0 kr.",
        "summary": "Fyrir hlaðvörp sem eru ekki með auglýsingar, kostun, greidda kynningu eða áskriftartekjur.",
        "features": [
            "Birting og grunnupplýsingar",
            "Venjulegt RSS flæði",
            "Engin tekjuöflun í þættinum",
        ],
        "status": "Tiltækt",
    },
    {
        "name": "Tekjuöflun",
        "label": "Fyrir kostun og auglýsingar",
        "price": "12.400 kr. / mán. með VSK",
        "summary": "Fyrir hlaðvörp sem afla tekna með auglýsingum, kostun, greiddri kynningu eða sambærilegu.",
        "features": [
            "Handvirk umsókn fyrst",
            "CEO/admin staðfestir skilmála",
            "Verð sýnt með VSK",
            "Greiðsluleið tengd síðar eftir samþykki",
        ],
        "status": "Handvirkt ferli",
        "featured": True,
    },
    {
        "name": "Fyrirtæki / stofnun",
        "label": "Fyrir rekstrar- eða vörumerkjahlaðvörp",
        "price": "Sérmat",
        "summary": "Fyrir aðila sem nota hlaðvarp sem hluta af atvinnustarfsemi, kynningu eða þjónustu.",
        "features": [
            "Sérsniðin yfirferð",
            "Reiknings- og tengiliðaupplýsingar",
            "Manual activation þar til billing er samþykkt",
        ],
        "status": "Samband fyrst",
    },
]


PRICING_PLANS = [
    {
        "slug": "hladvarp-free",
        "product": "Hlaðvarp",
        "name": "Okeypis hlaðvarp",
        "public_description": "Fyrir hlaðvörp án tekjuöflunar.",
        "gross_amount": 0,
        "cycle": "Engin gjaldfærsla",
        "visibility": "visible",
        "order": 10,
        "cta": "Halda áfram okeypis",
        "promo_note": "",
    },
    {
        "slug": "hladvarp-revenue",
        "product": "Hlaðvarp",
        "name": "Tekjuöflun",
        "public_description": "Fyrir kostun, auglýsingar og greidda kynningu.",
        "gross_amount": 12400,
        "cycle": "Mánaðarlega",
        "visibility": "visible",
        "order": 20,
        "cta": "Senda handvirka beiðni",
        "promo_note": "Operator getur skráð afslátt eða frítíma á viðskiptavinaspjaldi.",
    },
    {
        "slug": "hladvarp-business",
        "product": "Hlaðvarp",
        "name": "Fyrirtæki / stofnun",
        "public_description": "Sérmat fyrir rekstrar- eða vörumerkjahlaðvörp.",
        "gross_amount": 0,
        "cycle": "Sérmat",
        "visibility": "draft",
        "order": 30,
        "cta": "Bóka samtal",
        "promo_note": "Verð staðfest handvirkt fyrir reikning.",
    },
]


TRACKING_STATES = [
    "manual_pending",
    "manual_review",
    "manual_active",
    "paid",
    "unpaid",
    "needs_review",
    "waived",
    "cancelled",
    "invoiced_external",
    "provider_pending_later",
]


BILLING_CUSTOMERS = [
    {
        "slug": "kaffisopinn",
        "customer": "Kaffisopinn",
        "organization": "Kaffisopinn ehf.",
        "contact": "Hallur",
        "email": "operator@example.is",
        "product": "Hlaðvarp",
        "podcast": "Kaffisopinn",
        "storefront": "Hlaðvarp subscription page",
        "plan": "Tekjuöflun",
        "monetization": "Kostun / auglýsingar",
        "amount": 12400,
        "normal_amount": 12400,
        "discount_amount": 0,
        "free_until": "",
        "discount_reason": "",
        "cycle": "Mánaðarlega",
        "next_billing": "2026-07",
        "status": "needs_review",
        "billing_status": "unpaid",
        "review_status": "bookkeeper_review",
        "notes": "Prototype row. Confirm pricing, VAT, and Kontó wording before real invoice.",
        "notify": True,
        "audit": [
            "2026-07-08T11:00Z: Prototype application imported for operator review.",
            "2026-07-08T12:00Z: VAT-inclusive price rule applied.",
        ],
    },
    {
        "slug": "sveitastofa",
        "customer": "Sveitastofa",
        "organization": "Sveitastofa",
        "contact": "Ritstjórn",
        "email": "contact@example.is",
        "product": "Hlaðvarp",
        "podcast": "Sveitahljóð",
        "storefront": "Hlaðvarp subscription page",
        "plan": "Fyrirtæki / stofnun",
        "monetization": "Business podcast",
        "amount": 0,
        "normal_amount": 0,
        "discount_amount": 0,
        "free_until": "",
        "discount_reason": "",
        "cycle": "Manual quote",
        "next_billing": "2026-07",
        "status": "manual_pending",
        "billing_status": "not_ready",
        "review_status": "operator_review",
        "notes": "Needs manual review before amount is set.",
        "notify": True,
        "audit": [
            "2026-07-08T11:00Z: Awaiting quote before invoice draft.",
        ],
    },
    {
        "slug": "samfelagsrodd",
        "customer": "Samfélagsrödd",
        "organization": "Non-profit",
        "contact": "Umsjón",
        "email": "samfelag@example.is",
        "product": "Hlaðvarp",
        "podcast": "Samfélagsrödd",
        "storefront": "Hlaðvarp subscription page",
        "plan": "Okeypis hlaðvarp",
        "monetization": "None",
        "amount": 0,
        "normal_amount": 0,
        "discount_amount": 0,
        "free_until": "2026-08-01",
        "discount_reason": "Non-profit / no monetization in MVP review",
        "cycle": "No billing",
        "next_billing": "-",
        "status": "waived",
        "billing_status": "waived",
        "review_status": "transparent_waiver",
        "notes": "No monetization reported. Keep on review list if sponsorship starts.",
        "notify": False,
        "audit": [
            "2026-07-08T11:00Z: Waiver recorded with reason for review visibility.",
        ],
    },
]


OPERATOR_WORKFLOW = [
    "New podcast/application creates an operator notification.",
    "Operator reviews monetization and assigns plan/category.",
    "Operator records amount, next billing month, and manual status.",
    "Month-end report produces copyable/CSV invoice list for Kontó or other external invoicing.",
    "Payment status is updated manually after external payment/invoice confirmation.",
]


TIMEKEEPING_SETUP_STEPS = [
    {
        "title": "Opna örugga uppsetningu",
        "text": "Starfsmaður fær QR kóða eða stuttan tengikóða frá admin. Kóðinn er demo-only hér.",
        "meta": "Admin byrjar",
    },
    {
        "title": "Staðfesta síma",
        "text": "Síminn tengist starfsmanni, tæki og vinnustað án þess að birta lykla eða private config.",
        "meta": "Starfsmaður staðfestir",
    },
    {
        "title": "Velja lágmarksheimildir",
        "text": "MVP þarf bara atburði: inn, út, leiðréttingarbeiðni og samþykki. Ekki stöðugt eftirlit.",
        "meta": "Privacy-first",
    },
    {
        "title": "Prófa stimplun",
        "text": "Starfsmaður prófar innstimplun og sér núverandi stöðu strax á símanum.",
        "meta": "Tilbúið",
    },
]


TIMEKEEPING_HISTORY = [
    {"time": "08:04", "event": "Stimplað inn", "source": "Sími", "state": "Samþykkt"},
    {"time": "12:01", "event": "Matarhlé", "source": "Sími", "state": "Skráð"},
    {"time": "12:31", "event": "Til baka", "source": "Sími", "state": "Skráð"},
    {"time": "16:07", "event": "Stimplað út", "source": "Sími", "state": "Bíður yfirferðar"},
]


TIMEKEEPING_CORRECTIONS = [
    {
        "employee": "Demo starfsmaður",
        "request": "Gleymdi útstimplun í gær",
        "status": "Bíður samþykktar",
        "manager": "Yfirmaður",
    },
    {
        "employee": "Demo starfsmaður",
        "request": "Leiðrétta matarhlé",
        "status": "Samþykkt",
        "manager": "Yfirmaður",
    },
]


TIMEKEEPING_REPORTS = [
    {"label": "Í vinnu núna", "value": "1", "tone": "green"},
    {"label": "Bíður samþykktar", "value": "2", "tone": "amber"},
    {"label": "Klst. í viku", "value": "32,5", "tone": "blue"},
    {"label": "Frávik", "value": "1", "tone": "red"},
]


def askrift_hub(request):
    return render(request, "askrift/hub.html")


def timekeeping_demo(request):
    return render(
        request,
        "timekeeping/demo.html",
        {
            "setup_steps": TIMEKEEPING_SETUP_STEPS,
            "history": TIMEKEEPING_HISTORY,
            "corrections": TIMEKEEPING_CORRECTIONS,
            "reports": TIMEKEEPING_REPORTS,
        },
    )


@require_http_methods(["GET", "POST"])
def askrift_hladvarp(request):
    signup = None
    if request.method == "POST":
        signup = {
            "name": request.POST.get("name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "podcast": request.POST.get("podcast", "").strip(),
            "plan": request.POST.get("plan", "").strip(),
            "monetization": request.POST.get("monetization", "").strip(),
            "notes": request.POST.get("notes", "").strip(),
        }

    return render(
        request,
        "askrift/hladvarp.html",
        {
            "plans": SUBSCRIPTION_PLANS,
            "pricing_plans": enriched_pricing_plans(),
            "signup": signup,
            "tracking_states": TRACKING_STATES,
        },
    )


def enriched_customers():
    rows = []
    for row in BILLING_CUSTOMERS:
        item = row.copy()
        item.update(vat_breakdown(item["amount"]))
        item["final_amount"] = item["amount"]
        item["active_label"] = "Active" if item["status"] not in {"cancelled", "waived"} else "Inactive / waived"
        rows.append(item)
    return rows


def enriched_pricing_plans():
    rows = []
    for row in PRICING_PLANS:
        item = row.copy()
        item.update(vat_breakdown(item["gross_amount"]))
        rows.append(item)
    return sorted(rows, key=lambda item: item["order"])


def askrift_operator(request):
    customers = enriched_customers()
    billable = [row for row in customers if row["gross"] > 0 and row["status"] not in {"paid", "waived", "cancelled"}]
    review_count = sum(1 for row in customers if row["status"] in {"manual_pending", "needs_review", "unpaid"})
    total_due = sum(row["gross"] for row in billable)
    total_net = sum(row["net"] for row in billable)
    total_vat = sum(row["vat"] for row in billable)
    notifications = [row for row in customers if row["notify"]]

    return render(
        request,
        "askrift/operator.html",
        {
            "customers": customers,
            "notifications": notifications,
            "operator_workflow": OPERATOR_WORKFLOW,
            "review_count": review_count,
            "total_due": total_due,
            "total_net": total_net,
            "total_vat": total_vat,
            "tracking_states": TRACKING_STATES,
        },
    )


def askrift_customer_detail(request, slug):
    customer = next((row for row in enriched_customers() if row["slug"] == slug), None)
    if customer is None:
        raise Http404("Customer not found")
    return render(
        request,
        "askrift/customer_detail.html",
        {
            "customer": customer,
            "tracking_states": TRACKING_STATES,
        },
    )


@require_http_methods(["GET", "POST"])
def askrift_pricing_admin(request):
    preview = None
    if request.method == "POST":
        raw_amount = request.POST.get("gross_amount", "0").replace(".", "").replace(",", ".")
        try:
            gross_amount = Decimal(raw_amount)
        except Exception:
            gross_amount = Decimal("0")
        preview = {
            "product": request.POST.get("product", "").strip() or "Hlaðvarp",
            "name": request.POST.get("name", "").strip() or "Ný leið",
            "cycle": request.POST.get("cycle", "").strip() or "Mánaðarlega",
            "visibility": request.POST.get("visibility", "").strip() or "draft",
        }
        preview.update(vat_breakdown(gross_amount))

    return render(
        request,
        "askrift/pricing_admin.html",
        {
            "plans": enriched_pricing_plans(),
            "preview": preview,
            "vat_rate": int(VAT_RATE * 100),
        },
    )


def askrift_operator_export(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="manual-billing-report.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "customer",
            "organization",
            "contact",
            "email",
            "product",
            "podcast",
            "storefront",
            "plan",
            "monetization",
            "amount",
            "net_amount_for_invoice_tool",
            "vat_amount",
            "gross_customer_price",
            "vat_rate",
            "discount_amount",
            "free_until",
            "discount_reason",
            "cycle",
            "next_billing",
            "status",
            "billing_status",
            "review_status",
            "notes",
        ]
    )
    for row in enriched_customers():
        writer.writerow(
            [
                row["customer"],
                row["organization"],
                row["contact"],
                row["email"],
                row["product"],
                row["podcast"],
                row["storefront"],
                row["plan"],
                row["monetization"],
                row["amount"],
                row["net"],
                row["vat"],
                row["gross"],
                row["vat_rate"],
                row["discount_amount"],
                row["free_until"],
                row["discount_reason"],
                row["cycle"],
                row["next_billing"],
                row["status"],
                row["billing_status"],
                row["review_status"],
                row["notes"],
            ]
        )
    return response
