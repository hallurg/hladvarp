# CEO Directive — 8095 Raspberry Pi kiosk runtime

Date: 2026-08-01

The Raspberry Pi kiosk must not repeatedly refresh, restart Chromium, or reboot outside planned maintenance windows.

Approved runtime behavior:

- Content check every 60 seconds.
- Content-only delta updates.
- No full-page reload.
- Background and theme remain static throughout the day.
- Background/theme evaluation occurs once at local midnight (`Atlantic/Reykjavik`).
- Outside midnight, visual changes occur only after explicit CEO instruction.
- Failed API requests preserve the last-known-good display.
- No Pi reboot or browser restart except at planned and approved times.

Canonical implementation policy and incident record:

- `hallurg/kn-home-dashboard/docs/KIOSK_RUNTIME_POLICY.md`
- `hallurg/kn-home-dashboard/docs/incidents/2026-08-01-kiosk-refresh-loop.md`

Repository inspection found a two-minute poll in `static/live-refresh.js`, routine background/decorations handling in that polling path, and a separate 15-minute refresh constant in `static/screen.js`. Codex must trace browser-side and Pi-side restart/refresh behavior, prepare the minimal safe fix, run acceptance tests, and report controlled deployment readiness before production changes.
