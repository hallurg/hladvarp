# Project Memory

Last updated: 2026-07-06

## Context

The CEO asked Codex to operate as Engineering Director for Kaupfjelag software projects, including continuity, governance, launch gates, and concise CEO briefs.

## Important Operating Decisions

- Risky technical decisions must be respectfully challenged before implementation.
- Launch recommendations must be evidence-based.
- Missing state must be marked as missing, not invented.
- CEO should receive concise decision briefs rather than raw engineering noise.

## Recent Verified Work

### Hladvarp.com Review

On 2026-07-06, a launch review was performed on `72.62.212.222`.

Findings:

- Hladvarp containers were running.
- Castopod was healthy.
- Main public endpoints returned 200.
- Daily restic backup was successful.
- One previous listener API 500 had already been resolved; malformed JSON now returns 422.
- A test listener created during review was removed.

Launch recommendation:

- `GO WITH CONDITIONS`

Conditions:

- rotate temporary server password
- rotate exposed application/API secrets from the launch review context
- run pre-launch backup/restore validation

Port follow-up:

- `3000` belongs to Health Platform.
- Health Platform is not launch-ready and Foundation Validation is `NO-GO` for software implementation.
- On 2026-07-06, public `3000` was restricted by changing Health Platform Docker port binding from `0.0.0.0:3000` / `[::]:3000` to `127.0.0.1:3000`.
- Backup path: `/home/hallur/health-evidence-os/backups/20260706-173128-localhost-only-3000`.
- External access to `72.62.212.222:3000`, `hladvarp.com:3000`, and `www.hladvarp.com:3000` was no longer reachable after the change.
- `8080` belongs to `kennsluvefur`, a paused project.
- On 2026-07-06, a host guard was added to `kennsluvefur` so `hladvarp.com:8080` and `www.hladvarp.com:8080` redirect to canonical `https://hladvarp.com/`.
- After chief-of-staff review, public `8080` was restricted before launch by changing `kennsluvefur` Docker port binding to `127.0.0.1:8080:8080`.
- External access to `72.62.212.222:8080`, `hladvarp.com:8080`, and `www.hladvarp.com:8080` was no longer reachable after the change.

### Governance Baseline

On 2026-07-06, initial governance documents were created because the requested continuity documents were missing.

## Known Unknowns

- Which local repository is the canonical source for production Hladvarp.com customizations.
- Whether GitHub issues/PRs exist for this project.
- Whether the Kaupfjelag Django system is active, archived, or staging.
- Whether restore has been tested from restic.
