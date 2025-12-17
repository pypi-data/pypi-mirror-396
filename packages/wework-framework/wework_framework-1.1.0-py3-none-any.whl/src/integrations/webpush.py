import asyncio
import json
from typing import Optional

from pywebpush import webpush, WebPushException

from src.config.settings import settings
from src.db.repos import PushSubscriptionRepo
from src.db.models import Notification
from src.utils.logging import get_logger

logger = get_logger("webpush")


async def maybe_send_webpush_for_notification(notification: Notification) -> None:
    """Send Web Push for a notification if VAPID keys and subscriptions exist.

    این تابع اگر تنظیمات وب‌پوش یا سابسکرایب‌ها موجود نباشند، بی‌صدا از ارسال صرف‌نظر می‌کند.
    """
    if not settings.get("vapid_public_key") or not settings.get("vapid_private_key"):
        return

    repo = PushSubscriptionRepo()
    subs = await repo.list_for_user(notification.user_id)
    if not subs:
        return

    payload = {
        "title": notification.title,
        "body": notification.message,
        "link": notification.link or "",
        "type": notification.type,
    }

    vapid_claims = {
        "sub": settings.get("vapid_subject", "mailto:admin@example.com"),
    }

    async def _send_one(sub):
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh,
                "auth": sub.auth,
            },
        }
        try:
            await asyncio.to_thread(
                webpush,
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims=vapid_claims,
            )
        except WebPushException as exc:
            logger.warning("WebPush delivery failed for endpoint %s: %s", sub.endpoint, exc)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error sending WebPush: %s", exc)

    await asyncio.gather(*[_send_one(sub) for sub in subs])


