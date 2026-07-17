# Engineering Dashboard

Last updated: 2026-07-06

## Executive Status

Overall status: `GO WITH CONDITIONS` for Hladvarp.com launch, based on 2026-07-06 server review.

Latest hardening report: `docs/mission-alpha-prelaunch-hardening-report.md`.

## Active Workstreams

| Workstream | Status | Notes |
| --- | --- | --- |
| Governance baseline | In progress | Initial continuity documents created. |
| Hladvarp.com launch readiness | Go with conditions | Server healthy; pre-launch conditions remain. |
| Subscription policy engine | Board approved launch-safe mode | Runtime unchanged; docs now; implementation after launch in canonical repo. |
| Subscription billing activation | Post-launch design | Admin-visible and dry-run first; no live billing before billing launch gate. |
| Studio owner/admin UX | Staged rollout recommended | Owner dashboard should hide global counts; full redesign after launch. |
| Kaupfjelag Django system | Unknown | Local repository present, but no current milestone or tracked state. |
| Home dashboard | Unknown | Local folder present; server logs showed unrelated Caddy errors for screen dashboard. |

## Current Risks

| Priority | Risk | Status | Recommended Action |
| --- | --- | --- | --- |
| P0 | Temporary server password exposed in working context | Open | Rotate immediately. |
| P1 | Public ports `3000` and `8080` open | Resolved | `3000` Health Platform and `8080` paused project are now localhost-only. |
| P1 | Authenticated production content journey not run | Open | Use approved throwaway account/podcast/episode or accept launch without destructive production test. |
| P1 | Git baseline is untracked | Open | Decide repository ownership and create initial commit/branch policy. |
| P2 | Documentation encoding corruption | Open | Repair docs as a documentation task. |
| P2 | Multiple deploy directories on server | Open | Declare production source of truth. |

## Validation Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Infrastructure | Pass with conditions | Containers healthy; resources adequate. |
| Security | Conditional | HTTPS/security headers present; password rotation and open ports remain. |
| Backup | Pass with conditions | Restic backup succeeded; restore not proven. |
| Restore | Unknown | No restore drill observed. |
| Performance | Pass for smoke review | Endpoints responded quickly in curl checks. |
| Monitoring | Present | Uptime Kuma container running. |
| User journey | Partial | Public endpoints and listener API probes tested; real email/login journey still recommended. |
| Documentation | Conditional | Governance docs newly created; existing docs need encoding repair. |

## Decision Queue

1. Rotate server/sudo password.
2. Keep Health Platform `3000` localhost-only until Foundation Validation is no longer `NO-GO`.
3. Approve restore drill before public launch.
4. Decide whether this workspace is active source of truth or legacy/staging.
5. Approve post-launch Studio owner/admin dashboard split.
6. Identify canonical Hladvarp source repository/remote before subscription policy PR.
7. Select first billing/invoice/bank-claim provider to evaluate after launch.

## Recommended Next Task

Run a pre-launch hardening pass:

1. rotate temporary credentials
2. firewall or justify open ports
3. run a restore drill
4. record results in `VALIDATION_STATUS.md`
