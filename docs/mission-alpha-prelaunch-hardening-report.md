# Mission Alpha - Hladvarp.com Pre-Launch Hardening Report

Date: 2026-07-06
Status: `GO WITH CONDITIONS`

## Executive Summary

Mission Alpha launch-hardening was completed in launch-safe mode.

No Subscription & Feature Policy Engine was implemented.

No new business features were built.

No architecture refactor was performed.

Health Platform and the paused `kennsluvefur` project were restricted from public port exposure.

A named Restic pre-launch backup was completed:

- snapshot: `072fd83b`
- tag: `mission-alpha-prelaunch-20260706`
- log: `/opt/backups/mission-alpha-prelaunch-20260706.log`

## Recommendation

`GO WITH CONDITIONS`

Remaining conditions:

1. Rotate temporary server/sudo password and any exposed secrets.
2. CEO/operator must confirm launch-day monitoring notification path.
3. A real authenticated admin/operator content journey still needs human credentials or explicit approval to create test production content.

## Completed Actions

- Confirmed Hladvarp containers are running.
- Confirmed `hladvarp_castopod` is healthy.
- Confirmed public ports `3000` and `8080` are no longer reachable externally.
- Confirmed `3000` is localhost-only for Health Platform.
- Confirmed `8080` is localhost-only for `kennsluvefur`.
- Confirmed Hladvarp public home, podcast page, feed, episode page, login page, admin redirect, recorder health endpoint, RSS enclosure redirect, and final MP3 media response.
- Confirmed Uptime Kuma container is healthy.
- Confirmed Uptime Kuma monitors exist for Hladvarp.com and Kaffisopinn RSS.
- Confirmed latest Uptime Kuma heartbeats for those monitors are `200 - OK`.
- Completed named pre-launch Restic backup.

## Open Risks

- Temporary server/sudo password still needs rotation using a safe access-preserving procedure.
- Uptime Kuma has an unrelated failing SecureVault admin monitor with a misspelled hostname: `admin.securavault.is`.
- UFW still has an allow rule for `8095/tcp`, but no external listener was reachable during this pass.
- Full authenticated create-podcast/upload-episode path was not executed because it would create or alter production content without a dedicated test account/content approval.

## Exact Commands / Files Changed

Previously completed launch-hardening changes:

- `/home/hallur/kennsluvefur/src/server.js`
  - added host guard so `hladvarp.com:8080` redirects to canonical Hladvarp if reached locally/proxied
  - backup: `/home/hallur/kennsluvefur/backups/20260706-171658-host-guard/server.js.before-host-guard`

- `/home/hallur/kennsluvefur/docker-compose.yml`
  - changed public binding to `127.0.0.1:8080:8080`
  - backup: `/home/hallur/kennsluvefur/backups/20260706-172114-localhost-only-8080/docker-compose.yml.before-localhost-only`

- `/home/hallur/health-evidence-os/docker-compose.yml`
  - changed public binding to `127.0.0.1:${APP_PORT:-3000}:3000`
  - backup: `/home/hallur/health-evidence-os/backups/20260706-173128-localhost-only-3000`

Mission Alpha backup log created:

- `/opt/backups/mission-alpha-prelaunch-20260706.log`

## Public Port Status

Before hardening:

- `3000`: public, Health Platform, `0.0.0.0:3000`
- `8080`: public, `kennsluvefur`, `0.0.0.0:8080`

After hardening:

- `3000`: blocked externally, bound to `127.0.0.1:3000`
- `8080`: blocked externally, bound to `127.0.0.1:8080`
- `80`: public via Caddy
- `443`: public via Caddy
- `22`: public SSH
- `3478`: public Nextcloud Talk HPB

## Backup

Backup name/tag:

- `mission-alpha-prelaunch-20260706`

Snapshot:

- `072fd83b`

Location:

- Restic repository configured by `/root/.config/restic/nextcloud.env`

Log:

- `/opt/backups/mission-alpha-prelaunch-20260706.log`

Included Hladvarp scope:

- `/opt/hladvarp-stack`
- `/tmp/hladvarp.sql`
- Castopod media volume: `/var/lib/docker/volumes/hladvarp-stack_castopod_media/_data`

## User Journey Test Result

Launch-safe smoke journey result: `PASS WITH LIMITATIONS`

Verified:

- public home page: `200`
- new podcast application form: `200`
- login page: `200`
- admin studio unauthenticated redirect to login: `302`
- public podcast page: `200`
- RSS feed: `200`
- RSS feed contains 4 items for Kaffisopinn
- first episode page: `200`
- audio enclosure redirects to media URL: `307`
- final media URL returns `200 audio/mpeg`
- studio recorder health endpoint: `200`

Not executed:

- authenticated podcast creation
- authenticated episode upload

Reason:

- executing those steps would alter production content without a dedicated launch-test account and approved throwaway podcast/episode.

## Monitoring

Uptime Kuma:

- container: running, healthy
- public status endpoint: `https://status.hallur.net/` responds with `302` to `/dashboard`

Verified monitors:

- `Hladvarp.com` -> `https://www.hladvarp.com`
  - latest heartbeat: `200 - OK`
- `Kaffisopinn RSS` -> `https://hladvarp.com/@kaffisopinn/feed.xml`
  - latest heartbeat: `200 - OK`

Monitoring note:

- unrelated monitor `Secure Vault admin` is failing because it points to `https://admin.securavault.is`.

## Password Rotation Procedure

Do not rotate the server/sudo password blindly from this session unless a replacement credential and recovery path are confirmed.

Safe procedure:

1. Confirm at least one working SSH key or secondary sudo-capable admin account.
2. Open a second SSH session and keep the current session open.
3. Change password using `passwd hallur`.
4. Test a new SSH login in the second session.
5. Test `sudo -v` in the second session.
6. Confirm automation/deploy scripts do not depend on the old password.
7. Record rotation completion without storing the new password in repository or chat.

## Launch-Day Checklist

1. Confirm Hladvarp home/feed/login remain `200`.
2. Confirm `3000` and `8080` remain externally blocked.
3. Confirm Uptime Kuma Hladvarp monitors are green.
4. Keep a terminal ready for Caddy and Castopod logs.
5. Watch Hladvarp access/error logs during first hour.
6. Test one real email/login flow.
7. Keep backup snapshot `072fd83b` and restore runbook visible.
8. Do not enable subscription billing or policy enforcement.

## Refusals / Safety Decisions

- Refused to implement Subscription & Feature Policy Engine because launch-safe mode explicitly forbids it.
- Refused to build business/billing features before launch.
- Refused to run authenticated content creation/upload in production without a dedicated approved test account/content plan.
- Refused to rotate server password blindly because it could lock out deploy/runtime access without confirmed replacement access.
