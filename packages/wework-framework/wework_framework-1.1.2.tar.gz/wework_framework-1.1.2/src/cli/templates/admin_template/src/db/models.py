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

