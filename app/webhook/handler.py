"""GitHub webhook HTTP handler.

Receives GitHub webhook events, verifies the signature,
and dispatches to event-specific handlers.
"""

import hashlib
import hmac
import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.config import get_settings
from app.webhook.events import handle_pull_request_event

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhook"])


def _verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature (X-Hub-Signature-256)."""
    if not secret:
        logger.warning("GITHUB_WEBHOOK_SECRET is not set — skipping signature verification")
        return True

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@router.post("/webhook")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=""),
):
    """Receive and dispatch GitHub webhook events."""
    settings = get_settings()
    body = await request.body()

    # ── Signature verification ──
    if not _verify_signature(body, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    logger.info("Webhook received: event=%s action=%s", x_github_event, payload.get("action"))

    # ── Event dispatch ──
    if x_github_event == "pull_request":
        action = payload.get("action", "")
        if action in ("opened", "synchronize", "reopened"):
            background_tasks.add_task(handle_pull_request_event, payload)
            return {"status": "processing", "event": "pull_request", "action": action}

    elif x_github_event == "issue_comment":
        # Phase 3: conversation support
        logger.info("Issue comment event received — not yet implemented")
        return {"status": "skipped", "event": "issue_comment", "reason": "not implemented"}

    elif x_github_event == "ping":
        return {"status": "pong"}

    return {"status": "ignored", "event": x_github_event}
