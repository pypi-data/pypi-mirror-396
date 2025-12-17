"""
Database Models

Use 'wework make:model <ModelName>' to generate new models.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    Float,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """User model for authentication"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False, default="user", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SubscriptionPlan(Base):
    """Subscription plans"""

    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    max_accounts = Column(Integer, default=1)
    max_messages_per_day = Column(Integer, default=100)
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Subscription(Base):
    """User subscriptions"""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MessengerAccount(Base):
    """Messenger accounts connected by users"""

    __tablename__ = "messenger_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    messenger_type = Column(String, nullable=False, index=True)  # bale, eita, rubika, soroush, gap
    account_name = Column(String, nullable=False)
    account_phone = Column(String, nullable=True)
    credentials = Column(JSON, nullable=True)  # Store encrypted credentials
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MessageCampaign(Base):
    """Message campaigns for distributed sending"""

    __tablename__ = "message_campaigns"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    recipients = Column(JSON, nullable=False)  # List of phone numbers or user IDs
    account_ids = Column(JSON, nullable=False)  # List of messenger account IDs to use
    status = Column(String, default="pending")  # pending, sending, completed, failed
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class MessageLog(Base):
    """Message sending logs"""

    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("message_campaigns.id"), nullable=True, index=True)
    account_id = Column(Integer, ForeignKey("messenger_accounts.id"), nullable=False)
    recipient = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # sent, failed, pending
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

