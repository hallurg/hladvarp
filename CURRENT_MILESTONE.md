# Current Milestone

Last updated: 2026-07-06

## Milestone

Foundation and Launch Readiness Baseline

## Objective

Create minimum engineering continuity and governance so launch and follow-up work can proceed with traceability.

## Status

In progress.

## Subscription Policy Decision

The board requested a reusable Subscription & Feature Policy Engine on 2026-07-06.

Discovery found that Hladvarp already has partial policy-like runtime behavior for ad enablement and weekly episode quota, but the current local workspace is not the canonical Hladvarp source repository. Production code is mounted from `/opt/hladvarp-custom`.

Board decision: do not implement the full policy engine directly before launch. Use launch-safe mode only:

1. keep production runtime unchanged
2. preserve current ads/quota behavior
3. prepare pricing/commercial-use policy documentation for publication
4. create post-launch implementation plan
5. identify the canonical Hladvarp source repository/remote before any code PR
6. do not create code changes in the wrong workspace
7. continue launch checklist

Reference:

- `docs/subscription-policy-engine-brief.md`
- `docs/pricing-and-commercial-use-policy.md`
- `docs/subscription-feature-policy-engine.md`
- `docs/subscription-billing-activation-plan.md`

## Studio UX Decision

The Studio should be redesigned after launch so podcast owners see only their own podcast, plan/commercial status, usage limits, and next actions. Global platform counts belong on an admin-only operational dashboard.

Do not do a broad admin UX rewrite before launch. First post-launch patch should split owner dashboard from admin dashboard while preserving existing routes and forms.

Reference:

- `docs/hladvarp-studio-admin-ux-brief.md`

## Scope

- establish required continuity documents
- record verified project state
- record launch gate results
- define decision queue
- identify immediate launch conditions

## Acceptance Criteria

- `README_AI.md` exists
- `CURRENT_STATE.md` exists
- `ENGINEERING_DASHBOARD.md` exists
- `PROJECT_MEMORY.md` exists
- `ROADMAP.md` exists
- `ARCHITECTURE.md` exists
- `VALIDATION_STATUS.md` exists
- `THREAD_RESTART_SUMMARY.md` exists
- `docs/index.md` exists
- CEO has concise brief and recommended next action

## Next Milestone Candidate

Pre-launch hardening:

- credential rotation
- firewall review
- restore drill
- monitored real-user journey test
