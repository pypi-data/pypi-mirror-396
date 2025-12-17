from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Float,
    JSON,
    DateTime,
    Text,
    Boolean,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """Application user for authentication and subscriptions."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, nullable=True, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    username = Column(String, nullable=True, unique=True, index=True)  # Username for public profile
    bio = Column(Text, nullable=True)  # User bio/description
    avatar = Column(String, nullable=True)  # Avatar URL or path
    is_active = Column(Boolean, default=True)
    # roles: "user", "admin", "super_admin"
    role = Column(String, nullable=False, default="user", index=True)
    # Telegram notification settings
    telegram_enabled = Column(Boolean, default=False, nullable=False)
    telegram_bot_token = Column(String(512), nullable=True)  # User's Telegram bot token
    telegram_chat_id = Column(String(100), nullable=True)  # User's Telegram chat/channel ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    subscriptions = relationship("UserSubscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    otps = relationship("LoginOTP", back_populates="user")


class LoginOTP(Base):
    """One-time passwords sent via WECAN for login."""

    __tablename__ = "login_otps"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, nullable=False, index=True)
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", back_populates="otps")


class SubscriptionPlan(Base):
    """Base subscription plan definition (can be customized per user)."""

    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    # Example: {"max_items": 100, "priority_support": true, "custom_feature": true}
    features = Column(JSON, nullable=False, default={})
    base_price = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    """User's active or historical subscription instances."""

    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id = Column(
        Integer, ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True
    )
    # Customization of features per user (overrides plan.features)
    custom_features = Column(JSON, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="IRR")
    is_active = Column(Boolean, default=True)
    start_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")


class Payment(Base):
    """Payments performed via Zarinpal gateway."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    subscription_id = Column(
        Integer, ForeignKey("user_subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="IRR")
    # Zarinpal specific
    authority = Column(String, nullable=True, index=True)
    ref_id = Column(String, nullable=True, index=True)
    status = Column(
        String, nullable=False, default="pending"
    )  # pending, paid, failed, cancelled
    gateway_response = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="payments")
    subscription = relationship("UserSubscription", back_populates="payments")


class ConfigKV(Base):
    __tablename__ = "config_kv"
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(Text, nullable=True)


class Notification(Base):
    """In-app notifications (can also be mirrored to web push)."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(512), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="notifications", foreign_keys=[user_id])


class PushSubscription(Base):
    """Web Push subscription per user/browser."""

    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(String(512), nullable=False, unique=True)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="push_subscriptions", foreign_keys=[user_id])


