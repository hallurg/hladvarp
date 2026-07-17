from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Customer, Subscription
from .services import ensure_default_account_data


class AskriftAccountTests(TestCase):
    def test_default_hladvarp_storefront_renders(self):
        response = self.client.get(reverse("askrift_hladvarp"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hlaðvarp.com")
        self.assertContains(response, "Engin greiðsla er tekin")

    def test_manual_signup_creates_review_subscription_without_payment(self):
        product, _ = ensure_default_account_data()
        plan = product.plans.get(slug="tekjuoflun")

        response = self.client.post(
            reverse("askrift_hladvarp"),
            {
                "name": "Test User",
                "email": "test@example.is",
                "organization": "Test ehf.",
                "podcast": "Test hlaðvarp",
                "plan": plan.pk,
                "monetization": "ads",
                "notes": "Prófun",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), 1)
        subscription = Subscription.objects.get()
        self.assertEqual(subscription.status, Subscription.Status.MANUAL_PENDING)
        self.assertFalse(subscription.advertising_visible)
        self.assertEqual(subscription.payments.count(), 0)

    def test_advertising_entitlement_requires_paid_subscription(self):
        product, _ = ensure_default_account_data()
        plan = product.plans.get(slug="tekjuoflun")
        customer = Customer.objects.create(name="Paid", slug="paid", email="paid@example.is")
        subscription = Subscription.objects.create(customer=customer, product=product, plan=plan, status=Subscription.Status.MANUAL_ACTIVE)

        self.assertFalse(subscription.advertising_visible)

        subscription.status = Subscription.Status.PAID
        subscription.save()

        self.assertTrue(subscription.advertising_visible)

    def test_admin_dashboard_and_plan_list_render(self):
        response = self.client.get(reverse("askrift_admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account control room")

        response = self.client.get(reverse("askrift_admin_plans"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tekjuöflun")

    def test_plan_save_calculates_net_price(self):
        product, _ = ensure_default_account_data()
        plan = product.plans.get(slug="tekjuoflun")

        self.assertEqual(plan.gross_price, Decimal("12400.00"))
        self.assertEqual(plan.net_price, Decimal("10000.00"))
        self.assertEqual(plan.vat_amount, Decimal("2400.00"))
