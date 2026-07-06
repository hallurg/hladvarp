#!/usr/bin/env python3
"""KDS Codex wake bridge.

This script is intentionally small and conservative:

- It never executes text from GitHub comments as shell commands.
- It only reacts to allowed actors and explicit Codex/KDS wake wording.
- It can call an external Codex bridge webhook if CODEX_BRIDGE_WEBHOOK_URL is configured.
- If no backend is configured, it posts a clear GitHub acknowledgement for manual wake requests.
- Scheduled runs do not post comments unless a backend is configured, to avoid spam.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


WAKE_TOKENS = (
    "codex wake",
    "ceo heartbeat request",
    "codex master work order",
    "@codex",
    "codex:",
)

REPORT_TOKEN = "## codex engineering report"


@dataclass
class WakeContext:
    event_name: str
    repo: str
    actor: str
    issue_number: int
    command: str
    should_ack: bool
    should_dispatch: bool
    reason: str


def load_event() -> dict[str, Any]:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def workflow_dispatch_context(event: dict[str, Any]) -> WakeContext:
    inputs = event.get("inputs") or {}
    repo = (event.get("repository") or {}).get("full_name") or os.environ.get("GITHUB_REPOSITORY", "")
    actor = event.get("sender", {}).get("login") or os.environ.get("GITHUB_ACTOR", "")
    raw_issue = inputs.get("issue_number") or "7"
    try:
        issue_number = int(raw_issue)
    except ValueError:
        issue_number = 7
    command = inputs.get("command") or "Manual KDS wake request"
    return WakeContext(
        event_name="workflow_dispatch",
        repo=repo,
        actor=actor,
        issue_number=issue_number,
        command=command,
        should_ack=True,
        should_dispatch=True,
        reason="manual workflow_dispatch",
    )


def scheduled_context(event: dict[str, Any]) -> WakeContext:
    repo = (event.get("repository") or {}).get("full_name") or os.environ.get("GITHUB_REPOSITORY", "")
    actor = os.environ.get("GITHUB_ACTOR", "github-actions")
    return WakeContext(
        event_name="schedule",
        repo=repo,
        actor=actor,
        issue_number=7,
        command="Scheduled 4-hour KDS/Codex heartbeat",
        should_ack=False,
        should_dispatch=True,
        reason="scheduled heartbeat",
    )


def issue_comment_context(event: dict[str, Any]) -> WakeContext:
    repo = (event.get("repository") or {}).get("full_name") or os.environ.get("GITHUB_REPOSITORY", "")
    issue = event.get("issue") or {}
    comment = event.get("comment") or {}
    actor = (comment.get("user") or {}).get("login") or os.environ.get("GITHUB_ACTOR", "")
    issue_number = int(issue.get("number") or 7)
    body = str(comment.get("body") or "")
    body_l = body.lower()

    # Do not recursively treat actual reports as wake commands.
    if REPORT_TOKEN in body_l:
        return WakeContext(
            event_name="issue_comment",
            repo=repo,
            actor=actor,
            issue_number=issue_number,
            command=body,
            should_ack=False,
            should_dispatch=False,
            reason="comment is a Codex report, not a wake command",
        )

    should_dispatch = any(token in body_l for token in WAKE_TOKENS)
    return WakeContext(
        event_name="issue_comment",
        repo=repo,
        actor=actor,
        issue_number=issue_number,
        command=body,
        should_ack=should_dispatch,
        should_dispatch=should_dispatch,
        reason="matched wake token" if should_dispatch else "no wake token",
    )


def build_context(event: dict[str, Any]) -> WakeContext:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    if event_name == "workflow_dispatch":
        return workflow_dispatch_context(event)
    if event_name == "schedule":
        return scheduled_context(event)
    if event_name == "issue_comment":
        return issue_comment_context(event)
    repo = (event.get("repository") or {}).get("full_name") or os.environ.get("GITHUB_REPOSITORY", "")
    actor = event.get("sender", {}).get("login") or os.environ.get("GITHUB_ACTOR", "")
    return WakeContext(event_name, repo, actor, 7, "Unsupported event", False, False, "unsupported event")


def actor_allowed(actor: str) -> bool:
    allowed_raw = os.environ.get("KDS_ALLOWED_ACTORS", "hallurg")
    allowed = {item.strip().lower() for item in allowed_raw.split(",") if item.strip()}
    return "*" in allowed or actor.lower() in allowed


def github_api(repo: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not available")
    url = f"https://api.github.com/repos/{repo}{path}"
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def post_issue_comment(ctx: WakeContext, body: str) -> None:
    github_api(ctx.repo, f"/issues/{ctx.issue_number}/comments", {"body": body})


def dispatch_to_webhook(ctx: WakeContext) -> tuple[bool, str]:
    webhook_url = os.environ.get("CODEX_BRIDGE_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return False, "CODEX_BRIDGE_WEBHOOK_URL is not configured"

    payload = {
        "source": "github-actions:kds-codex-wake-bridge",
        "event_name": ctx.event_name,
        "repository": ctx.repo,
        "actor": ctx.actor,
        "issue_number": ctx.issue_number,
        "command": ctx.command,
        "reason": ctx.reason,
        "timestamp": int(time.time()),
        "required_report_marker": "## CODEX ENGINEERING REPORT",
        "safety": {
            "do_not_expose_secrets": True,
            "do_not_rotate_credentials_without_access_continuity": True,
            "start_with_issue": 4,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "kds-codex-wake-bridge",
    }
    secret = os.environ.get("CODEX_BRIDGE_SHARED_SECRET", "")
    if secret:
        signature = hmac.new(secret.encode("utf-8"), data, hashlib.sha256).hexdigest()
        headers["X-KDS-Signature-256"] = f"sha256={signature}"

    request = urllib.request.Request(webhook_url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            text = response.read().decode("utf-8", errors="replace")[:400]
            if 200 <= status < 300:
                return True, f"Webhook accepted request with HTTP {status}. {text}"
            return False, f"Webhook returned HTTP {status}. {text}"
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")[:400]
        return False, f"Webhook HTTP error {exc.code}. {text}"
    except Exception as exc:  # noqa: BLE001 - report bridge failure without exposing secrets
        return False, f"Webhook dispatch failed: {type(exc).__name__}: {exc}"


def main() -> int:
    event = load_event()
    ctx = build_context(event)

    print(f"KDS wake bridge event={ctx.event_name} actor={ctx.actor} issue={ctx.issue_number} reason={ctx.reason}")

    if not actor_allowed(ctx.actor) and ctx.event_name != "schedule":
        print(f"Actor {ctx.actor!r} is not allowed to trigger the bridge.")
        return 0

    if not ctx.should_dispatch:
        print("No dispatch needed.")
        return 0

    ok, detail = dispatch_to_webhook(ctx)
    print(detail)

    if ctx.event_name == "schedule" and not os.environ.get("CODEX_BRIDGE_WEBHOOK_URL", "").strip():
        print("Scheduled heartbeat no-op because no webhook is configured.")
        return 0

    if ctx.should_ack:
        if ok:
            body = (
                "## KDS WAKE BRIDGE ACK\n\n"
                "GitHub received the Codex wake request and dispatched it to the configured Codex bridge backend.\n\n"
                "Expected next artifact: `## CODEX ENGINEERING REPORT`.\n\n"
                "Safety reminder: no secrets should be posted in GitHub or chat."
            )
        else:
            body = (
                "## KDS WAKE BRIDGE ACK — backend not active\n\n"
                "GitHub received the Codex wake request, but no Codex bridge backend is active yet.\n\n"
                f"Status: `{detail}`\n\n"
                "Required setup: configure `CODEX_BRIDGE_WEBHOOK_URL` as a repository secret, "
                "or connect GitHub Agent/Codex monitoring directly.\n\n"
                "Until then, use manual Codex invocation with: `Read hallurg/hladvarp issue #7 and execute the Master Work Order, starting with #4.`"
            )
        post_issue_comment(ctx, body)

    return 0 if ok or not os.environ.get("CODEX_BRIDGE_WEBHOOK_URL", "").strip() else 1


if __name__ == "__main__":
    sys.exit(main())
