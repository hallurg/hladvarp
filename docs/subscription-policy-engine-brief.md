# Subscription & Feature Policy Engine - Engineering Brief

Date: 2026-07-06
Status: `STAGED ROLLOUT RECOMMENDED`

## Decision

Do not implement the full Subscription & Feature Policy Engine directly into production before the public Hladvarp.com launch.

Recommended launch-safe path:

1. Keep the current runtime behavior stable for launch.
2. Document the pricing and commercial-use policy now.
3. After launch, implement a central policy service in a proper Hladvarp source repository with branch, tests, migration scripts, review, and rollback.
4. Later extract product-neutral concepts for SecureVault, Health Platform, Kaupfjelag.com, and future products.

## Current Architecture Summary

Verified production architecture:

- Public site: `https://hladvarp.com`
- Runtime: Castopod 2.0.0-beta.5 container
- Reverse proxy: Caddy
- Database: MariaDB
- Cache: Redis
- Custom Hladvarp code is mounted from `/opt/hladvarp-custom`
- Static front page is mounted from `/opt/hladvarp-front`
- Production compose file: `/opt/hladvarp-stack/docker-compose.yml`

Relevant custom module:

- `/opt/hladvarp-custom/modules/HladvarpStudio`

Relevant controller:

- `Modules\HladvarpStudio\Controllers\StudioController`

Relevant public application controller:

- `Modules\HladvarpStudio\Controllers\PodcastApplicationController`

## Discovery Findings

### Data Model

Castopod core tables are prefixed with `cp_`.

Existing Hladvarp custom tables include:

- `cp_hladvarp_podcast_billing_profiles`
- `cp_hladvarp_podcast_episode_quotas`
- `cp_hladvarp_podcast_lifecycle`
- `cp_hladvarp_ad_campaigns`
- `cp_hladvarp_ad_placements`
- `cp_hladvarp_podcast_applications`
- `cp_hladvarp_user_profiles`
- `cp_hladvarp_user_permissions`

There are also legacy/unprefixed custom tables visible in the database. These should be audited before any schema expansion.

### Existing Policy-Like Behavior

The system already has partial policy behavior:

- default weekly episode limit is `3`
- per-podcast weekly episode quotas are stored in `hladvarp_podcast_episode_quotas`
- ad enablement is stored in `hladvarp_podcast_billing_profiles.ads_enabled`
- ad campaigns cannot be attached to a podcast unless that podcast is marked ad-enabled
- active ad audio is only injected when the podcast is ad-enabled
- recorder receives an `adsAllowed` parameter derived from podcast ad enablement

This is useful launch functionality, but it is not yet a reusable policy engine.

### Authentication And Ownership

Authentication is handled by CodeIgniter Shield / Castopod auth.

Podcast access uses Castopod podcast authorization helpers and permission filters:

- `permission:admin.access`
- `permission:podcast#.edit`
- `permission:podcast#.episodes.edit`
- `permission:podcast#.episodes.delete`

Podcast ownership and edit access should not be re-modeled before launch.

### Admin UI

Hladvarp Studio already has admin areas for:

- podcasts
- episodes
- users
- ads
- distribution
- SEO
- announcements
- podcast applications

This is the safest eventual integration surface for admin-visible plan and entitlement status.

### Billing / Payment Readiness

No safe payment-provider integration was verified.

Do not implement payment processing before launch.

Do not claim kennitala verification. Existing national ID fields are self-declared.

## Recommended Data Model

Post-launch, add a small product-neutral policy layer with these concepts:

- `SubscriptionPlan`
- `FeatureKey`
- `FeaturePolicy`
- `AccountEntitlement`
- `PodcastEntitlement`
- `UsageLimit`
- `CommercialUseDeclaration`

For Hladvarp, store runtime state at podcast/account level:

- plan key: `free`, `creator`, `business`, `enterprise`
- commercial declaration flags
- admin review status
- manual override fields
- policy metadata as JSON where low risk

Avoid scattered checks like `if plan == business`.

## Safest Integration Point

The safest post-launch integration point is a service class inside the Hladvarp Studio module, for example:

- `Modules\HladvarpStudio\Services\SubscriptionPolicyService`

Public API:

- `hasFeature($subject, string $featureKey): bool`
- `getLimit($subject, string $limitKey): int|string|null`
- `assertFeature($subject, string $featureKey): void`
- `assertWithinLimit($subject, string $limitKey, int $currentUsage): void`
- `getPlan($subject): string`

Existing helpers should then be migrated behind the service:

- `podcastAdsEnabled`
- `podcastWeeklyEpisodeLimit`
- `defaultWeeklyEpisodeLimit`
- ad creation checks
- recorder `adsAllowed`
- episode schedule quota checks

## Tables / Models Needed

Minimal post-launch schema:

- `hladvarp_subscription_plans`
- `hladvarp_feature_policies`
- `hladvarp_account_entitlements`
- `hladvarp_podcast_entitlements`
- `hladvarp_commercial_use_declarations`

Launch-safe alternative:

- extend `hladvarp_podcast_billing_profiles` only after backup and migration review
- treat existing `ads_enabled` and episode quota as the current policy source

## Files That Would Change

Expected post-launch files:

- `modules/HladvarpStudio/Services/SubscriptionPolicyService.php`
- `modules/HladvarpStudio/Controllers/StudioController.php`
- `modules/HladvarpStudio/Controllers/PodcastApplicationController.php`
- `modules/HladvarpStudio/Config/Routes.php` if a policy admin screen is added
- Hladvarp Studio views/forms generated by `StudioController`
- documentation in `docs/`

## Migration Risk

Risk: medium to high before launch.

Reasons:

- production source is mounted directly under `/opt/hladvarp-custom`
- no clean local Hladvarp code repository was found in the current workspace
- no branch/PR path was verified for this code
- custom tables are created imperatively via `ensureTables()`
- both prefixed and unprefixed Hladvarp custom tables are visible
- policy changes affect podcast creation, episode upload, ad setup, and recorder behavior

## Launch Risk

Full implementation before launch is not recommended.

Likely failure modes:

- podcast creation/editing blocked by new policy defaults
- episode upload blocked by migration or quota bug
- ads/recorder behavior changes unexpectedly
- admin users lose visibility or control of podcasts
- production schema drift without rollback-tested migrations

## Rollback Plan

For any post-launch implementation:

1. take a named database and media backup
2. copy all changed files under `/opt/hladvarp-custom/backups/<timestamp>-subscription-policy-engine/`
3. apply schema changes using additive `CREATE TABLE IF NOT EXISTS` / `ensureColumn` only
4. deploy with enforcement initially in warn/admin-flag mode
5. verify public pages, RSS feeds, login, podcast edit, episode upload, recorder, and ad flow
6. rollback by restoring previous mounted files and clearing any new enforcement toggles

## Safe Now

Before launch:

- keep existing ad enablement and weekly quota behavior
- document pricing and commercial-use policy
- add admin operating note: commercial podcasts must be marked ad-enabled / paid-plan candidate manually
- do not add payment integration
- do not add national registry lookup
- do not claim kennitala verification

## After Launch

Implement central policy service around existing behavior:

- FREE cannot use `podcast.ads.allowed`
- CREATOR can use ads/sponsorships
- BUSINESS can enable business metadata/manual support flags
- ENTERPRISE can use manual override
- unknown feature fails closed
- missing plan defaults safely to FREE

Start with admin-visible status and warn-only enforcement, then progressively enforce.

## Later Platform Extraction

After Hladvarp proves the model, extract product-neutral concepts for:

- SecureVault
- Health Platform
- Kaupfjelag.com
- future Kaupfjelag products

Do not copy Hladvarp-specific podcast logic into those products. Reuse only the neutral policy concepts and service contract.
