# KDS Codex Wake Bridge

This document describes the GitHub-side wake bridge for the Kaupfjelag Development System (KDS).

## Purpose

The bridge gives GitHub a real operational role in the Codex workflow:

1. CEO/ChatGPT/Codex posts an explicit wake or heartbeat request in GitHub.
2. GitHub Actions receives the event.
3. The bridge validates that the actor and wording are allowed.
4. The bridge dispatches to a configured Codex backend webhook when available.
5. The bridge writes an acknowledgement back to GitHub for manual wake requests.

This makes silence visible. If the backend is not configured, GitHub says so instead of pretending Codex was woken.

## Workflow

File:

```text
.github/workflows/kds-codex-wake-bridge.yml
```

Triggers:

- `issue_comment` when an explicit Codex/KDS wake phrase is posted
- `workflow_dispatch` for manual triggering from GitHub Actions
- `schedule` every 4 hours for heartbeat dispatch

## Trigger phrases

The issue-comment path reacts to explicit wording such as:

```text
CODEX WAKE
CEO HEARTBEAT REQUEST
CODEX MASTER WORK ORDER
@codex
Codex:
```

Actual Codex reports starting with:

```text
## CODEX ENGINEERING REPORT
```

are ignored by the bridge to avoid loops.

## Required report marker

Codex periodic reports must still begin with:

```text
## CODEX ENGINEERING REPORT
```

ChatGPT uses that marker to find Engineering Reports and convert them to CEO Briefs.

## Repository secrets

The bridge can operate in two modes.

### Mode A — visible acknowledgement only

No extra secret is configured.

GitHub will acknowledge wake requests and say the Codex backend is not active yet. This is useful because it proves GitHub Actions received the command.

### Mode B — dispatch to Codex backend

Configure these repository secrets:

```text
CODEX_BRIDGE_WEBHOOK_URL
CODEX_BRIDGE_SHARED_SECRET
```

`CODEX_BRIDGE_WEBHOOK_URL` should point to a trusted service that knows how to wake Codex or hand the task to the Codex runtime.

`CODEX_BRIDGE_SHARED_SECRET` is optional but recommended. When present, the bridge signs the request body with HMAC-SHA256 and sends the signature in:

```text
X-KDS-Signature-256
```

## Security rules

- Do not put passwords, API keys, SMTP credentials, or tokens into GitHub comments.
- Do not run GitHub comment text as shell commands.
- Do not rotate credentials unless access continuity is proven first.
- Only allowed actors should be able to trigger the bridge.
- The default allowed actor is `hallurg`.
- The scheduled run does not post comments when no backend is configured, to avoid spam.

## Current KDS target

The bridge exists to support the current operating flow:

1. Codex starts with issue #4 — Mission Alpha launch gates.
2. Codex then handles #5 — subscription entrypoint discovery.
3. Codex then handles #6 — Revenue Gate subscription MVP by 2026-08-01.
4. Codex reports to GitHub.
5. ChatGPT reads reports and returns CEO Briefs.

## Manual fallback

If no backend is configured, use the manual fallback:

```text
Read hallurg/hladvarp issue #7 and execute the Master Work Order, starting with #4.
```

## Definition of done

The wake bridge is considered fully active when:

- GitHub Actions runs on wake comments.
- A wake request posts acknowledgement.
- `CODEX_BRIDGE_WEBHOOK_URL` is configured or GitHub Agent/Codex monitoring is confirmed.
- Codex responds by posting `## CODEX ENGINEERING REPORT` on the relevant issue.
