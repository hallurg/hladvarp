# Subscription Billing Activation Plan

Date: 2026-07-06
Status: `POST-LAUNCH DESIGN - DO NOT ENABLE BILLING YET`

## Decision

Hladvarp.com should support a visible, admin-manageable subscription system before billing is activated.

The system must allow administrators to:

- see available plans
- see each podcast/account subscription status
- set a podcast/account to Free, Creator, Business, or Enterprise
- mark commercial-use declaration status
- prepare billing metadata
- configure a future billing provider
- run billing in test/dry-run mode
- activate billing only after explicit approval

No automatic invoice, claim, payment request, or bank/billing-provider action should run before a dedicated billing launch gate is passed.

## Product Requirement

The CEO needs to be able to see the subscription system before it is launched and start it when all requirements are ready.

The system should eventually support automatic integration with:

- an invoicing provider
- a bank claim/payment request provider
- or both, depending on Icelandic operational fit

The purpose is to create invoices or payment claims for subscribers based on their active plan and billing status.

## Launch-Safe Mode

Before billing launch:

- subscription plans may be visible to admins
- plan assignment may be stored as metadata
- commercial-use status may be reviewed manually
- billing provider settings may be drafted but not active
- invoices/claims must not be sent automatically
- all billing actions must be disabled or dry-run only

Suggested admin status labels:

- `Not configured`
- `Configured - inactive`
- `Test mode`
- `Ready for approval`
- `Active`
- `Paused`

## Activation Model

Billing activation should require all of the following:

1. Canonical Hladvarp source repository identified.
2. Subscription policy service implemented and tested.
3. Billing provider selected.
4. Test/sandbox credentials configured.
5. Dry-run invoice/claim generation verified.
6. Manual approval workflow verified.
7. Backup and rollback plan documented.
8. CEO approval recorded.
9. Production credentials added securely.
10. First real billing run executed manually and monitored.

## Provider Integration Requirements

The billing integration must support:

- provider type
- provider environment: test/sandbox/production
- account/customer identifier
- invoice reference
- claim/payment due date
- amount
- currency
- VAT/tax metadata if applicable
- line items
- status sync
- error logging
- retry policy
- manual resend/cancel controls

## Provider Abstraction

Use a provider adapter interface so Hladvarp is not locked into one billing company or bank integration.

Suggested contract:

```php
createCustomer(array $customer): BillingCustomerResult
createInvoice(array $invoice): BillingInvoiceResult
createClaim(array $claim): BillingClaimResult
cancelInvoice(string $externalId): BillingActionResult
syncStatus(string $externalId): BillingStatusResult
```

All production calls must go through this adapter.

Do not scatter direct API calls to a billing provider through controllers.

## Data To Store

Minimum future fields:

- subscription plan
- billing status
- billing provider
- provider customer ID
- provider invoice/claim IDs
- billing contact name
- billing contact email
- billing national ID / company ID
- billing address if required
- billing cycle
- next billing date
- last billing run
- tax/VAT metadata if applicable
- manual billing notes

Do not claim national ID verification unless a real verification process exists.

## Safety Controls

Required controls:

- feature flag: `billing.enabled`
- feature flag: `billing.dry_run`
- environment flag: `billing.provider_environment`
- admin permission for billing activation
- audit log for every billing action
- preview before send
- manual first-run approval
- provider error dashboard
- idempotency keys for invoice/claim creation

## Admin UX

Admin should be able to see:

- plan catalog
- subscription status per podcast/account
- commercial-use declaration
- billing readiness
- provider connection status
- next billing action
- dry-run preview
- historical invoices/claims
- errors requiring attention

Podcast owners should be able to see:

- current plan
- commercial-use status
- whether billing is active
- upcoming amount if billing is active
- contact/support path

Owners should not see internal provider configuration.

## Things Not To Build Yet

Do not build before approval:

- live provider integration
- automatic claim creation
- automatic invoice emailing
- production payment collection
- national registry lookup
- automatic suspension for unpaid invoices
- AI-based ad/commercial detection

## Billing Launch Gate

Return `GO`, `GO WITH CONDITIONS`, or `NO-GO` before enabling billing.

Gate checklist:

- legal/commercial wording approved
- pricing approved
- provider selected
- sandbox test passed
- dry-run output reviewed
- rollback documented
- audit logging verified
- support process ready
- CEO approval recorded

## Rollback

Rollback must be possible without affecting podcast publishing.

Minimum rollback:

1. set `billing.enabled=false`
2. keep subscription metadata visible
3. stop scheduled billing jobs
4. prevent new invoice/claim provider calls
5. preserve audit history
6. manually reconcile any provider-side objects already created

## CEO Decisions Required

- Which billing provider or bank should be evaluated first?
- Should Hladvarp start with invoices, bank claims, or both?
- Should the first billing run be manual only?
- Who approves a podcast moving from Free to paid commercial status?
- What grace period applies before any enforcement?
