"""Seeder for default subscription plans."""
import asyncio
from typing import List, Dict, Any

from sqlalchemy import select

from src.db.base import AsyncSessionLocal
from src.db.models import SubscriptionPlan


# Default subscription plans shown in pricing/landing page
DEFAULT_PLANS: List[Dict[str, Any]] = [
    {
        "name": "Free",
        "description": "پلن رایگان برای شروع و تست پلتفرم.",
        "features": {
            "max_strategies": 1,
            "max_backtests_per_day": 10,
            "priority_support": False,
        },
        "base_price": 0.0,
        "is_active": True,
        "is_default": True,
    },
    {
        "name": "Pro",
        "description": "پلن حرفه‌ای برای تریدرهایی که چند استراتژی همزمان دارند.",
        "features": {
            "max_strategies": 5,
            "max_backtests_per_day": 50,
            "priority_support": True,
        },
        "base_price": 390000.0,
        "is_active": True,
        "is_default": False,
    },
    {
        "name": "Enterprise",
        "description": "پلن سازمانی با ظرفیت بالا و پشتیبانی ویژه.",
        "features": {
            "max_strategies": 20,
            "max_backtests_per_day": 200,
            "priority_support": True,
        },
        "base_price": 990000.0,
        "is_active": True,
        "is_default": False,
    },
]


async def seed_subscription_plans():
    """Insert default subscription plans if they don't already exist."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SubscriptionPlan))
        existing_plans = result.scalars().all()
        existing_names = {p.name for p in existing_plans}

        created_count = 0
        updated_default_count = 0
        skipped_count = 0

        # Ensure only one default plan (if multiple are marked is_default in code)
        default_plan_name = next(
            (p["name"] for p in DEFAULT_PLANS if p.get("is_default")), None
        )

        for plan_data in DEFAULT_PLANS:
            name = plan_data["name"]
            if name in existing_names:
                print(f"⏭️  Plan '{name}' already exists, skipping create...")
                skipped_count += 1
                continue

            plan = SubscriptionPlan(
                name=plan_data["name"],
                description=plan_data.get("description"),
                features=plan_data.get("features") or {},
                base_price=plan_data.get("base_price", 0.0),
                is_active=plan_data.get("is_active", True),
                is_default=plan_data.get("is_default", False),
            )
            session.add(plan)
            created_count += 1
            print(f"✅ Created subscription plan: {plan.name}")

        # Normalize default plan flag: only one default
        if default_plan_name:
            result = await session.execute(select(SubscriptionPlan))
            plans = result.scalars().all()
            for p in plans:
                should_be_default = p.name == default_plan_name
                if p.is_default != should_be_default:
                    p.is_default = should_be_default
                    updated_default_count += 1
            if updated_default_count:
                print(
                    f"ℹ️  Updated default flags for {updated_default_count} plan(s) "
                    f"(default: '{default_plan_name}')."
                )

        await session.commit()

        print("\n📊 Summary:")
        print(f"   Created: {created_count}")
        print(f"   Skipped (already existed): {skipped_count}")


async def clear_subscription_plans():
    """Remove only the default seeded subscription plans (by name)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SubscriptionPlan))
        plans = result.scalars().all()
        seed_plan_names = {p["name"] for p in DEFAULT_PLANS}

        deleted_count = 0
        for plan in plans:
            if plan.name in seed_plan_names:
                await session.delete(plan)
                deleted_count += 1
                print(f"🗑️  Deleted subscription plan: {plan.name}")

        await session.commit()
        print(f"✅ Deleted {deleted_count} subscription plans from seed list.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        asyncio.run(clear_subscription_plans())
    else:
        asyncio.run(seed_subscription_plans())


