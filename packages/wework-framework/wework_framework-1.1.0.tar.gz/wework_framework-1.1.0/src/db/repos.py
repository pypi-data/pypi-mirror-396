import asyncio

from .base import AsyncSessionLocal
from .models import (
    ConfigKV,
    Notification,
    PushSubscription,
)
from sqlalchemy import select, func
from typing import List, Optional


class ConfigRepo:
    async def list_configs(self):
        async with AsyncSessionLocal() as session:
            q = await session.execute(select(ConfigKV))
            return [{'key': r.key, 'value': r.value} for r in q.scalars().all()]

    async def upsert_config(self, key, value):
        async with AsyncSessionLocal() as session:
            q = await session.execute(select(ConfigKV).filter_by(key=key))
            found = q.scalars().first()
            if found:
                found.value = value
                session.add(found)
            else:
                session.add(ConfigKV(key=key, value=value))
            await session.commit()


class NotificationRepo:
    async def create(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
    ) -> Notification:
        async with AsyncSessionLocal() as session:
            notif = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                link=link,
            )
            session.add(notif)
            await session.commit()
            await session.refresh(notif)

        # بعد از ذخیره در دیتابیس، تلاش برای ارسال وب‌پوش (بدون شکست زدن تراکنش)
        try:
            from src.integrations.webpush import maybe_send_webpush_for_notification

            await maybe_send_webpush_for_notification(notif)
        except Exception:
            # خطای وب‌پوش نباید مسیر اصلی را خراب کند
            pass

        return notif

    async def bulk_create(
        self,
        user_ids: list[int],
        type: str,
        title: str,
        message: str,
        link: Optional[str] = None,
    ) -> List[Notification]:
        """Create notifications for multiple users in one transaction."""
        if not user_ids:
            return []

        unique_ids = list({uid for uid in user_ids if uid is not None})
        if not unique_ids:
            return []

        async with AsyncSessionLocal() as session:
            notifs = [
                Notification(
                    user_id=uid,
                    type=type,
                    title=title,
                    message=message,
                    link=link,
                )
                for uid in unique_ids
            ]
            session.add_all(notifs)
            await session.commit()
            for n in notifs:
                await session.refresh(n)

        # ارسال وب‌پوش پس از کامیت تا مسیر اصلی کند نشود
        try:
            from src.integrations.webpush import maybe_send_webpush_for_notification

            await asyncio.gather(
                *[maybe_send_webpush_for_notification(n) for n in notifs]
            )
        except Exception:
            pass

        return notifs

    async def list_for_user(
        self, user_id: int, limit: int = 50, offset: int = 0, unread_only: bool = False
    ) -> List[Notification]:
        async with AsyncSessionLocal() as session:
            query = select(Notification).where(Notification.user_id == user_id)
            if unread_only:
                query = query.where(Notification.is_read == False)  # noqa: E712
            query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
            q = await session.execute(query)
            return list(q.scalars().all())

    async def count_unread(self, user_id: int) -> int:
        async with AsyncSessionLocal() as session:
            q = await session.execute(
                select(func.count(Notification.id)).where(
                    Notification.user_id == user_id,
                    Notification.is_read == False,  # noqa: E712
                )
            )
            return int(q.scalar() or 0)

    async def mark_read(self, user_id: int, notif_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            q = await session.execute(
                select(Notification).where(
                    Notification.id == notif_id,
                    Notification.user_id == user_id,
                )
            )
            notif = q.scalar_one_or_none()
            if not notif:
                return False
            notif.is_read = True
            session.add(notif)
            await session.commit()
            return True

    async def mark_all_read(self, user_id: int) -> int:
        async with AsyncSessionLocal() as session:
            q = await session.execute(
                select(Notification).where(
                    Notification.user_id == user_id,
                    Notification.is_read == False,  # noqa: E712
                )
            )
            notifs = q.scalars().all()
            count = len(notifs)
            if notifs:
                for n in notifs:
                    n.is_read = True
                    session.add(n)
                await session.commit()
            return count


class PushSubscriptionRepo:
    async def upsert_subscription(
        self,
        user_id: int,
        endpoint: str,
        p256dh: str,
        auth: str,
        user_agent: Optional[str] = None,
    ) -> PushSubscription:
        async with AsyncSessionLocal() as session:
            q = await session.execute(
                select(PushSubscription).where(PushSubscription.endpoint == endpoint)
            )
            sub = q.scalar_one_or_none()
            if sub:
                sub.user_id = user_id
                sub.p256dh = p256dh
                sub.auth = auth
                sub.user_agent = user_agent
            else:
                sub = PushSubscription(
                    user_id=user_id,
                    endpoint=endpoint,
                    p256dh=p256dh,
                    auth=auth,
                    user_agent=user_agent,
                )
                session.add(sub)
            await session.commit()
            await session.refresh(sub)
            return sub

    async def list_for_user(self, user_id: int) -> List[PushSubscription]:
        async with AsyncSessionLocal() as session:
            q = await session.execute(
                select(PushSubscription).where(PushSubscription.user_id == user_id)
            )
            return list(q.scalars().all())
