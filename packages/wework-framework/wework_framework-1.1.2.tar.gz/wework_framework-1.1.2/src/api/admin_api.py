from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, validator
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.api.auth_api import get_current_admin, get_role_info
from src.db.base import AsyncSessionLocal
from src.db.models import (
    ConfigKV,
    Payment,
    SubscriptionPlan,
    User,
    UserSubscription,
)
from src.db.repos import NotificationRepo


router = APIRouter(prefix="/api/admin", tags=["admin"])

notification_repo = NotificationRepo()


class AdminNotificationPayload(BaseModel):
    title: str
    message: str
    type: str = "system"
    link: Optional[str] = None
    user_ids: Optional[List[int]] = None
    send_to_all: bool = False

    @validator("title")
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("عنوان اعلان الزامی است.")
        cleaned = v.strip()
        if len(cleaned) > 255:
            raise ValueError("طول عنوان نباید بیش از 255 کاراکتر باشد.")
        return cleaned

    @validator("message")
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("متن اعلان الزامی است.")
        cleaned = v.strip()
        if len(cleaned) > 4000:
            raise ValueError("طول پیام نباید بیش از 4000 کاراکتر باشد.")
        return cleaned

    @validator("type")
    def validate_type(cls, v: str) -> str:
        if not v or not v.strip():
            return "system"
        cleaned = v.strip()
        return cleaned[:50]

    @validator("user_ids", pre=True)
    def normalize_user_ids(cls, v):
        if v is None:
            return None
        if isinstance(v, (list, tuple, set)):
            ids: list[int] = []
            for item in v:
                try:
                    ids.append(int(item))
                except (TypeError, ValueError):
                    continue
            return ids
        return None


@router.get("/overview")
async def admin_overview(current_admin=Depends(get_current_admin)):
    """Basic overview of users and payments (legacy endpoint kept for compatibility)."""
    async with AsyncSessionLocal() as session:
        users_q = await session.execute(select(User))
        users = users_q.scalars().all()

        payments_q = await session.execute(select(Payment))
        payments = payments_q.scalars().all()

    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "phone_number": u.phone_number,
                "full_name": u.full_name,
                "role": get_role_info(u.role),
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ],
        "payments": [
            {
                "id": p.id,
                "user_email": next(
                    (u.email for u in users if u.id == p.user_id), None
                ),
                "amount": p.amount,
                "status": p.status,
                "ref_id": p.ref_id,
                "paid_at": p.paid_at,
            }
            for p in payments
        ],
    }


@router.get("/stats")
async def admin_stats(current_admin=Depends(get_current_admin)):
    """High-level KPIs for the admin dashboard."""
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)

    async with AsyncSessionLocal() as session:
        total_users_q = await session.execute(select(func.count(User.id)))
        total_users = total_users_q.scalar_one() or 0

        active_users_q = await session.execute(
            select(func.count(User.id)).where(User.is_active.is_(True))
        )
        active_users = active_users_q.scalar_one() or 0

        admins_q = await session.execute(
            select(func.count(User.id)).where(User.role.in_(("admin", "super_admin")))
        )
        admins_count = admins_q.scalar_one() or 0

        total_revenue_q = await session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                Payment.status == "paid"
            )
        )
        total_revenue = float(total_revenue_q.scalar_one() or 0.0)

        active_subs_q = await session.execute(
            select(func.count(UserSubscription.id)).where(
                UserSubscription.is_active.is_(True)
            )
        )
        active_subscriptions = active_subs_q.scalar_one() or 0

        plans_q = await session.execute(
            select(func.count(SubscriptionPlan.id)).where(
                SubscriptionPlan.is_active.is_(True)
            )
        )
        active_plans = plans_q.scalar_one() or 0

        config_count_q = await session.execute(
            select(func.count(ConfigKV.id))
        )
        config_items = config_count_q.scalar_one() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "admins_count": admins_count,
        "total_revenue": total_revenue,
        "active_subscriptions": active_subscriptions,
        "active_plans": active_plans,
        "config_items": config_items,
    }


@router.get("/users")
async def list_users(
    current_admin=Depends(get_current_admin),
    search: str | None = Query(default=None, description="Email, phone or name"),
    is_active: bool | None = Query(default=None),
    role: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Paginated, filterable list of users for admin management."""
    async with AsyncSessionLocal() as session:
        base_query = select(User)
        if search:
            like = f"%{search}%"
            base_query = base_query.where(
                (User.email.ilike(like))
                | (User.phone_number.ilike(like))
                | (User.full_name.ilike(like))
            )
        if is_active is not None:
            base_query = base_query.where(User.is_active.is_(is_active))
        if role:
            base_query = base_query.where(User.role == role)

        total_q = await session.execute(
            base_query.with_only_columns(func.count(User.id)).order_by(None)
        )
        total = total_q.scalar_one() or 0

        users_q = await session.execute(
            base_query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        users = users_q.scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "phone_number": u.phone_number,
                "full_name": u.full_name,
                "role": get_role_info(u.role),
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }


@router.patch("/users/{user_id}")
async def update_user_admin(
    user_id: int,
    payload: Dict[str, Any],
    current_admin=Depends(get_current_admin),
):
    """Update user fields from admin panel (role, is_active, full_name, phone_number, email)."""
    allowed_fields = {"role", "is_active", "full_name", "phone_number", "email"}
    unexpected = set(payload.keys()) - allowed_fields
    if unexpected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"فیلدهای نامعتبر: {', '.join(unexpected)}",
        )

    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="کاربر یافت نشد.",
            )

        if "role" in payload:
            new_role = payload["role"]
            if new_role not in {"user", "admin", "super_admin"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="نقش نامعتبر است.",
                )
            # فقط super_admin می‌تواند نقش را به super_admin تغییر دهد
            if new_role == "super_admin" and current_admin.role != "super_admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="فقط سوپر ادمین می‌تواند نقش را به سوپر ادمین تغییر دهد.",
                )
            user.role = new_role
        if "is_active" in payload:
            user.is_active = bool(payload["is_active"])
        if "full_name" in payload:
            user.full_name = payload["full_name"]
        if "phone_number" in payload:
            user.phone_number = payload["phone_number"]
        if "email" in payload:
            # ایمیل را به صورت lowercase ذخیره می‌کنیم تا یکتا بودن و جستجو راحت‌تر شود
            user.email = (payload["email"] or "").strip().lower()

        session.add(user)
        await session.commit()
        await session.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
        "full_name": user.full_name,
        "role": get_role_info(user.role),
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.post("/notifications/send")
async def admin_send_notifications(
    payload: AdminNotificationPayload,
    current_admin=Depends(get_current_admin),
):
    """Send an in-app + web push notification to all active users or selected users."""
    target_user_ids: list[int] = []
    skipped_user_ids: list[int] = []

    async with AsyncSessionLocal() as session:
        if payload.send_to_all:
            q = await session.execute(
                select(User.id).where(User.is_active.is_(True))
            )
            target_user_ids = [row[0] for row in q.all() if row[0] is not None]
        else:
            requested_ids = sorted(set(payload.user_ids or []))
            if not requested_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="برای ارسال هدف خاص، حداقل یک کاربر لازم است.",
                )

            q = await session.execute(
                select(User.id, User.is_active).where(User.id.in_(requested_ids))
            )
            rows = q.all()
            found_ids = {row[0] for row in rows}
            inactive_ids = {row[0] for row in rows if not row[1]}

            target_user_ids = [row[0] for row in rows if row[1]]
            skipped_user_ids = sorted((set(requested_ids) - found_ids) | inactive_ids)

        if not target_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="کاربر فعالی برای ارسال اعلان یافت نشد.",
            )

    created = await notification_repo.bulk_create(
        user_ids=target_user_ids,
        type=payload.type,
        title=payload.title,
        message=payload.message,
        link=payload.link,
    )

    return {
        "target_count": len(target_user_ids),
        "created_count": len(created),
        "skipped_user_ids": skipped_user_ids,
        "send_to_all": payload.send_to_all,
        "type": payload.type,
    }


@router.get("/subscriptions")
async def admin_subscriptions(current_admin=Depends(get_current_admin)):
    """Overview of user subscriptions and plans for admin dashboard."""
    async with AsyncSessionLocal() as session:
        subs_q = await session.execute(
            select(UserSubscription)
            .options(joinedload(UserSubscription.user), joinedload(UserSubscription.plan))
            .order_by(UserSubscription.created_at.desc())
        )
        subs = subs_q.scalars().all()

    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "user_email": s.user.email if s.user else None,
            "plan_id": s.plan_id,
            "plan_name": s.plan.name if s.plan else None,
            "price": s.price,
            "currency": s.currency,
            "is_active": s.is_active,
            "start_at": s.start_at,
            "end_at": s.end_at,
        }
        for s in subs
    ]


@router.get("/plans")
async def admin_plans(current_admin=Depends(get_current_admin)):
    """List subscription plans."""
    async with AsyncSessionLocal() as session:
        plans_q = await session.execute(
            select(SubscriptionPlan).order_by(SubscriptionPlan.created_at.desc())
        )
        plans = plans_q.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "features": p.features,
            "base_price": p.base_price,
            "is_active": p.is_active,
            "is_default": p.is_default,
            "created_at": p.created_at,
        }
        for p in plans
    ]


@router.get("/health")
async def admin_health(current_admin=Depends(get_current_admin)):
    """Operational health summary based on recent activity."""
    now = datetime.now(timezone.utc)
    last_7d = now - timedelta(days=7)

    async with AsyncSessionLocal() as session:
        # Payments
        pay_total_q = await session.execute(select(func.count(Payment.id)))
        payments_total = pay_total_q.scalar_one() or 0

        pay_failed_q = await session.execute(
            select(func.count(Payment.id)).where(
                Payment.status.in_(("failed", "cancelled"))
            )
        )
        payments_failed = pay_failed_q.scalar_one() or 0

        pay_7d_q = await session.execute(
            select(func.count(Payment.id)).where(Payment.created_at >= last_7d)
        )
        payments_last_7d = pay_7d_q.scalar_one() or 0

        # Users
        users_total_q = await session.execute(select(func.count(User.id)))
        users_total = users_total_q.scalar_one() or 0

        active_users_q = await session.execute(
            select(func.count(User.id)).where(User.is_active.is_(True))
        )
        active_users = active_users_q.scalar_one() or 0

    return {
        "payments": {
            "total": payments_total,
            "failed": payments_failed,
            "last_7d": payments_last_7d,
        },
        "users": {
            "total": users_total,
            "active": active_users,
        },
    }


@router.get("/config")
async def admin_config_list(current_admin=Depends(get_current_admin)):
    """List key-value configuration items stored in ConfigKV."""
    async with AsyncSessionLocal() as session:
        cfg_q = await session.execute(select(ConfigKV).order_by(ConfigKV.key.asc()))
        items = cfg_q.scalars().all()

    return [
        {
            "id": c.id,
            "key": c.key,
            "value": c.value,
        }
        for c in items
    ]


@router.put("/config/{config_id}")
async def admin_config_update(
    config_id: int,
    payload: Dict[str, Any],
    current_admin=Depends(get_current_admin),
):
    """Update a single config item value from admin panel."""
    if "value" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فیلد value الزامی است.",
        )

    async with AsyncSessionLocal() as session:
        q = await session.execute(select(ConfigKV).where(ConfigKV.id == config_id))
        item = q.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="آیتم تنظیمات یافت نشد.",
            )

        item.value = str(payload["value"])
        session.add(item)
        await session.commit()
        await session.refresh(item)

    return {
        "id": item.id,
        "key": item.key,
        "value": item.value,
    }



