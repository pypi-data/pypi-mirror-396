from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.api.auth_api import get_current_active_user
from src.config.settings import settings
from src.db.base import AsyncSessionLocal
from src.db.models import SubscriptionPlan, UserSubscription, Payment, User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.db.repos import NotificationRepo


router = APIRouter(prefix="/api/billing", tags=["billing"])

notification_repo = NotificationRepo()


class PlanPreviewRequest(BaseModel):
    base_plan_id: int
    # Customization knobs come from UI
    custom_features: Dict[str, Any]


class PlanPreviewResponse(BaseModel):
    base_price: float
    final_price: float
    currency: str = "IRR"
    features: Dict[str, Any]


def _build_frontend_url(path: str, params: Dict[str, Any]) -> str:
    base = settings.frontend_base_url or "http://localhost:5173"
    normalized_path = path if path.startswith("/") else f"/{path}"
    query = urlencode({k: str(v) for k, v in params.items() if v is not None})
    return f"{base}{normalized_path}" + (f"?{query}" if query else "")


def _payment_redirect(
    success: bool,
    payment_id: int,
    extra_params: Optional[Dict[str, Any]] = None,
) -> RedirectResponse:
    params: Dict[str, Any] = {"payment_id": payment_id, "status": "paid" if success else "failed"}
    if extra_params:
        params.update({k: v for k, v in extra_params.items() if v is not None})
    path = settings.payment_success_path if success else settings.payment_failure_path
    return RedirectResponse(_build_frontend_url(path, params), status_code=303)


def _serialize_payment(payment: Payment) -> Dict[str, Any]:
    plan = payment.subscription.plan if payment.subscription and payment.subscription.plan else None
    return {
        "id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "currency": payment.currency,
        "ref_id": payment.ref_id,
        "authority": payment.authority,
        "description": payment.description,
        "subscription_id": payment.subscription_id,
        "plan_id": plan.id if plan else None,
        "plan_name": plan.name if plan else None,
        "paid_at": payment.paid_at,
        "created_at": payment.created_at,
    }


async def _get_plan(plan_id: int) -> SubscriptionPlan:
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
        plan = q.scalar_one_or_none()
        if not plan or not plan.is_active:
            raise HTTPException(status_code=404, detail="پلن پیدا نشد یا غیرفعال است.")
        return plan


@router.get("/plans")
async def list_plans():
    """List active subscription plans (for landing/pricing page)."""
    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.is_active == True)  # noqa: E712
        )
        plans = q.scalars().all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "features": p.features,
                "base_price": p.base_price,
                "is_default": p.is_default,
            }
            for p in plans
        ]


@router.post("/plans/preview", response_model=PlanPreviewResponse)
async def preview_custom_plan(payload: PlanPreviewRequest):
    """Calculate price for a customized plan based on base plan features."""
    plan = await _get_plan(payload.base_plan_id)
    base_features = plan.features or {}

    # Simple pricing rule example – you can adjust logic as needed
    final_features = {**base_features, **(payload.custom_features or {})}
    price = plan.base_price

    priority_support = bool(final_features.get("priority_support", False))
    if priority_support and not base_features.get("priority_support", False):
        price += 50000

    if price < 0:
        price = 0

    return PlanPreviewResponse(
        base_price=plan.base_price,
        final_price=price,
        currency="IRR",
        features=final_features,
    )


@router.post("/checkout/zarinpal")
async def start_zarinpal_checkout(
    payload: PlanPreviewRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Create a user subscription + payment and redirect URL for Zarinpal (sandbox)."""
    plan = await _get_plan(payload.base_plan_id)
    preview = await preview_custom_plan(payload)

    async with AsyncSessionLocal() as session:
        subscription = UserSubscription(
            user_id=current_user.id,
            plan_id=plan.id,
            custom_features=preview.features,
            price=preview.final_price,
            currency=preview.currency,
            is_active=False,
        )
        session.add(subscription)
        await session.flush()

        payment = Payment(
            user_id=current_user.id,
            subscription_id=subscription.id,
            amount=preview.final_price,
            currency=preview.currency,
            status="pending",
            description=f"Subscription purchase for plan {plan.name}",
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)

    merchant_id = settings.zarinpal_merchant_id
    if not merchant_id:
        raise HTTPException(
            status_code=500,
            detail="Zarinpal merchant ID تنظیم نشده است. لطفا در .env مقدار ZARINPAL_MERCHANT_ID را پر کنید.",
        )

    request_url = (
        "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
        if settings.zarinpal_sandbox
        else "https://api.zarinpal.com/pg/v4/payment/request.json"
    )

    callback_url = f"{settings.zarinpal_callback_url}?payment_id={payment.id}"

    request_data = {
        "merchant_id": merchant_id,
        "amount": int(preview.final_price),
        "callback_url": callback_url,
        "description": f"خرید اشتراک پلن {plan.name}",
        "metadata": {"email": current_user.email, "mobile": current_user.phone_number},
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(request_url, json=request_data)
        data = resp.json()

    if data.get("data") and data["data"].get("authority"):
        authority = data["data"]["authority"]
        async with AsyncSessionLocal() as session:
            q = await session.execute(select(Payment).where(Payment.id == payment.id))
            db_payment = q.scalar_one()
            db_payment.authority = authority
            db_payment.gateway_response = data
            session.add(db_payment)
            await session.commit()

        start_pay_base = (
            "https://sandbox.zarinpal.com/pg/StartPay/"
            if settings.zarinpal_sandbox
            else "https://www.zarinpal.com/pg/StartPay/"
        )
        return {
            "payment_id": payment.id,
            "authority": authority,
            "start_pay_url": f"{start_pay_base}{authority}",
        }

    raise HTTPException(
        status_code=400,
        detail=f"خطا در ایجاد تراکنش زرین‌پال: {data.get('errors') or data}",
    )


@router.get("/zarinpal/callback")
async def zarinpal_callback(
    Authority: str = Query(...),
    Status: str = Query(...),
    payment_id: int = Query(...),
):
    """Callback URL that Zarinpal redirects to (sandbox or production)."""
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Payment).where(Payment.id == payment_id))
        payment = q.scalar_one_or_none()
        if not payment or payment.authority != Authority:
            raise HTTPException(status_code=404, detail="تراکنش پیدا نشد.")

    if Status != "OK":
        async with AsyncSessionLocal() as session:
            q = await session.execute(select(Payment).where(Payment.id == payment_id))
            db_payment = q.scalar_one()
            db_payment.status = "failed"
            db_payment.gateway_response = {"status": Status}
            session.add(db_payment)
            await session.commit()
        return _payment_redirect(
            success=False,
            payment_id=payment_id,
            extra_params={
                "message": "پرداخت توسط کاربر لغو شد یا ناموفق بود.",
                "gateway_status": Status,
            },
        )

    verify_url = (
        "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        if settings.zarinpal_sandbox
        else "https://api.zarinpal.com/pg/v4/payment/verify.json"
    )

    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Payment).where(Payment.id == payment_id))
        payment = q.scalar_one()

    request_data = {
        "merchant_id": settings.zarinpal_merchant_id,
        "amount": int(payment.amount),
        "authority": Authority,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(verify_url, json=request_data)
        data = resp.json()

    code = data.get("data", {}).get("code")
    if code == 100:
        ref_id = data["data"]["ref_id"]
        async with AsyncSessionLocal() as session:
            q = await session.execute(select(Payment).where(Payment.id == payment_id))
            db_payment = q.scalar_one()
            db_payment.status = "paid"
            db_payment.ref_id = str(ref_id)
            db_payment.paid_at = datetime.now(timezone.utc)
            db_payment.gateway_response = data
            session.add(db_payment)

            # Activate subscription (if this payment is for a plan)
            if db_payment.subscription_id:
                q2 = await session.execute(
                    select(UserSubscription).where(
                        UserSubscription.id == db_payment.subscription_id
                    )
                )
                sub = q2.scalar_one()
                sub.is_active = True
                sub.start_at = datetime.now(timezone.utc)
                sub.end_at = datetime.now(timezone.utc) + timedelta(days=30)
                session.add(sub)

            await session.commit()

        return _payment_redirect(
            success=True,
            payment_id=payment_id,
            extra_params={
                "ref_id": ref_id,
                "message": "پرداخت با موفقیت انجام شد.",
            },
        )

    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Payment).where(Payment.id == payment_id))
        db_payment = q.scalar_one()
        db_payment.status = "failed"
        db_payment.gateway_response = data
        session.add(db_payment)
        await session.commit()

    return _payment_redirect(
        success=False,
        payment_id=payment_id,
        extra_params={
            "message": "تایید پرداخت ناموفق بود.",
            "gateway_code": code,
        },
    )


@router.get("/me/subscription")
async def get_my_subscription(current_user: User = Depends(get_current_active_user)):
    """Return current active subscription and features for logged-in user."""
    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == current_user.id,
                UserSubscription.is_active == True,  # noqa: E712
            )
            .order_by(UserSubscription.start_at.desc())
        )
        sub = q.scalar_one_or_none()
        if not sub:
            return {"active": False}

        plan_features = sub.plan.features if sub.plan and sub.plan.features else {}
        features = {**plan_features, **(sub.custom_features or {})}
        return {
            "active": True,
            "subscription_id": sub.id,
            "plan_name": sub.plan.name if sub.plan else None,
            "features": features,
            "price": sub.price,
            "currency": sub.currency,
            "start_at": sub.start_at,
            "end_at": sub.end_at,
        }


@router.get("/me/payments")
async def list_my_payments(current_user: User = Depends(get_current_active_user)):
    """Return payment history for the authenticated user."""
    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(Payment)
            .options(
                selectinload(Payment.subscription).selectinload(UserSubscription.plan)
            )
            .where(Payment.user_id == current_user.id)
            .order_by(Payment.created_at.desc())
        )
        payments = q.scalars().all()

    return {"payments": [_serialize_payment(payment) for payment in payments]}


@router.get("/payments/{payment_id}")
async def get_payment_details(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Return a single payment details for the owner user."""
    async with AsyncSessionLocal() as session:
        q = await session.execute(
            select(Payment)
            .options(
                selectinload(Payment.subscription).selectinload(UserSubscription.plan)
            )
            .where(Payment.id == payment_id)
        )
        payment = q.scalar_one_or_none()
        if not payment or payment.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="پرداخت یافت نشد.")

    return _serialize_payment(payment)


