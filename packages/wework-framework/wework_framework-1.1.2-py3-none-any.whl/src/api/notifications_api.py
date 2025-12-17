from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.auth_api import get_current_active_user
from src.db.models import User
from src.db.repos import NotificationRepo, PushSubscriptionRepo


router = APIRouter(prefix="/api/notifications", tags=["notifications"])

notification_repo = NotificationRepo()
push_repo = PushSubscriptionRepo()


class NotificationOut(BaseModel):
  id: int
  type: str
  title: str
  message: str
  link: Optional[str]
  is_read: bool
  created_at: str


class PushSubscriptionIn(BaseModel):
  endpoint: str
  p256dh: str
  auth: str
  user_agent: Optional[str] = None


@router.get("", response_model=List[NotificationOut])
async def list_notifications(
  limit: int = 20,
  offset: int = 0,
  unread_only: bool = False,
  current_user: User = Depends(get_current_active_user),
):
  items = await notification_repo.list_for_user(
    user_id=current_user.id, limit=limit, offset=offset, unread_only=unread_only
  )
  return [
    NotificationOut(
      id=n.id,
      type=n.type,
      title=n.title,
      message=n.message,
      link=n.link,
      is_read=n.is_read,
      created_at=n.created_at.isoformat() if n.created_at else "",
    )
    for n in items
  ]


@router.get("/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_active_user)):
  count = await notification_repo.count_unread(current_user.id)
  return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
  notification_id: int, current_user: User = Depends(get_current_active_user)
):
  ok = await notification_repo.mark_read(current_user.id, notification_id)
  if not ok:
    raise HTTPException(status_code=404, detail="Notification not found")
  return {"status": "ok"}


@router.post("/read-all")
async def mark_all_notifications_read(
  current_user: User = Depends(get_current_active_user),
):
  count = await notification_repo.mark_all_read(current_user.id)
  return {"status": "ok", "count": count}


@router.post("/push-subscriptions")
async def register_push_subscription(
  payload: PushSubscriptionIn,
  current_user: User = Depends(get_current_active_user),
):
  await push_repo.upsert_subscription(
    user_id=current_user.id,
    endpoint=payload.endpoint,
    p256dh=payload.p256dh,
    auth=payload.auth,
    user_agent=payload.user_agent,
  )
  return {"status": "ok"}


