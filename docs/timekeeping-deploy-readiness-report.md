# Timekeeping Deploy Readiness Report

Report timestamp: 2026-07-17T19:52:11Z UTC / 2026-07-17 19:52 Atlantic/Reykjavik.

## Scope

This report covers the KN Timekeeping / Starfsmannahald canonical workspace foundation after the approved local continuation from Mission Control #10.

Approved local scope:

- move the local MVP into a canonical repository/workspace;
- add real authentication and device pairing foundations;
- add idempotent Bixby/mobile event ingest design and implementation;
- prepare deploy-readiness reporting.

## Current State

- Canonical local workspace: this Django project under `starfsfolk`.
- Authentication foundation: existing Django/DRF authenticated API flow is required for timekeeping endpoints.
- Device pairing foundation: employees create a device record, receive a one-time visible pairing code, connect the device, and can revoke it.
- Event audit foundation: timekeeping actions are append-only `TimaklukkuAtburdur` records.
- Idempotent mobile ingest: `/api/starfsfolk/maetingar/mobile_ingest/` requires an authenticated user, active paired device, `client_event_id`, and `event_type` of `IN` or `OUT`.
- Duplicate Bixby/mobile submissions with the same `client_event_id` return the original event and do not create another event.

## GO / NO-GO

GO:

- continue local implementation;
- run local tests;
- extend auth/session/device-pairing design in this workspace;
- prepare API documentation and acceptance criteria.

NO-GO:

- production deploy;
- production migrations;
- live data changes;
- server secret work;
- `.env` changes;
- Caddy, Docker, proxy, firewall, backup or upload changes;
- commit, push, merge, or release without explicit approval.

## Verification Required Before Any Production Request

- Full Django test suite passing with the target settings profile.
- Migration plan reviewed against the production database state.
- Auth/session model reviewed for shared-device and lost-device cases.
- Bixby/mobile retry behavior tested from real client flows.
- Admin revocation flow verified after a device is compromised or replaced.
- Rollback plan written for schema and API rollout.
- Separate CEO GO requested and granted before production deployment.
