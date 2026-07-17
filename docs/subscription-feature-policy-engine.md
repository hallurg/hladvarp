# Subscription & Feature Policy Engine

Status: concept and staged implementation plan

## Purpose

The Subscription & Feature Policy Engine is intended to give Kaupfjelag projects one central way to answer:

- what plan an account or object is on
- which features are allowed
- which limits apply
- whether manual entitlements override default plan behavior
- what is active runtime behavior versus pricing metadata or planned functionality

The first implementation should happen in Hladvarp.com, but the model should remain reusable by future Kaupfjelag systems.

## Core Concepts

### SubscriptionPlan

Examples:

- `free`
- `creator`
- `business`
- `enterprise`

### FeatureKey

Examples:

- `podcast.ads.allowed`
- `podcast.sponsorships.allowed`
- `podcast.max_episodes_per_week`
- `podcast.max_admins`
- `podcast.custom_domain`
- `podcast.advanced_analytics`
- `podcast.api_access`
- `podcast.priority_support`
- `podcast.unlimited_uploads`
- `podcast.storage_limit_gb`
- `podcast.max_rss_feeds`
- `podcast.private_feeds`

For future products, use product namespaces:

- `securevault.retention_policy.custom`
- `securevault.private_intake.allowed`
- `health_platform.evidence_review.workflow`
- `kaupfjelag.accounting.export`

### FeaturePolicy

Defines what a plan includes by default.

Unknown features must fail closed.

### Entitlement

Defines account-specific or object-specific overrides.

Examples:

- account entitlement
- podcast entitlement
- organization entitlement
- project entitlement

### UsageLimit

Defines numeric limits.

Examples:

- episodes per week
- storage quota
- number of admins
- number of feeds
- number of private feeds

### CommercialUseDeclaration

For Hladvarp, this captures whether a podcast/account declares:

- ads
- sponsorships
- paid promotion
- commercial affiliation
- paid subscription
- other monetization

Self-declaration and admin review should come before automated policing.

## Service Contract

All runtime checks should go through one central helper/service:

```php
hasFeature($subject, string $featureKey): bool
getLimit($subject, string $limitKey): mixed
assertFeature($subject, string $featureKey): void
assertWithinLimit($subject, string $limitKey, int $currentUsage): void
getPlan($subject): string
```

Do not scatter checks like `if ($plan === 'business')`.

## Hladvarp Adapter

Hladvarp-specific code may translate podcast state into product-neutral policy decisions.

Examples:

- `ads_enabled` becomes `podcast.ads.allowed`
- weekly episode quota becomes `podcast.max_episodes_per_week`
- admin-selected plan becomes default policy profile
- manual override can allow or deny individual features

## Reuse In Other Projects

### SecureVault

Potential features:

- private intake
- storage retention
- audit export
- admin seats
- organization-level encryption policy

### Health Platform

Potential features:

- evidence workspace count
- reviewer roles
- provenance export
- advanced analytics
- regulated workflow flags

Medical/scientific governance must remain separate from billing. A paid plan must never imply clinical validity.

### Kaupfjelag.com

Potential features:

- organization pages
- staff seats
- accounting integrations
- custom domains
- reporting exports

## Implementation Rule

Start small:

1. model the existing behavior
2. centralize checks
3. expose admin-visible status
4. enforce only low-risk rules
5. add payment integration later only after explicit approval

The platform service should grow from proven project needs, not from speculative feature lists.
