"""
Database Models - SQLAlchemy
============================
Credit-based licensing with user accounts and purchase tracking.
"""

import uuid
import secrets
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean,
    ForeignKey, Numeric, Date, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# ============================================
# CREDIT-BASED SYSTEM (One-Time Purchases)
# ============================================

class User(Base):
    """
    User accounts - identified by email.
    Credits are the primary currency.
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identity
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    
    # Credits (server is authoritative)
    credits_balance = Column(Integer, default=250, nullable=False)  # Start with 250 free
    credits_total_purchased = Column(Integer, default=0)
    credits_total_used = Column(Integer, default=0)
    
    # Authentication (last order key)
    last_order_id = Column(String(255))  # For email + order auth
    auth_token = Column(String(255), unique=True, index=True)  # Session token
    
    # Status
    is_free_tier = Column(Boolean, default=True)
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)
    last_sync_at = Column(DateTime)
    
    # Relationships
    purchases = relationship("CreditPurchase", back_populates="user")
    credit_usage = relationship("CreditUsage", back_populates="user")
    
    def generate_auth_token(self) -> str:
        """Generate a new auth token."""
        self.auth_token = secrets.token_urlsafe(32)
        return self.auth_token


class CreditPurchase(Base):
    """
    Track all credit purchases from Lemon Squeezy.
    Each order creates one record.
    """
    __tablename__ = "credit_purchases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Lemon Squeezy data
    order_id = Column(String(255), unique=True, nullable=False, index=True)
    variant_id = Column(String(255))
    product_name = Column(String(255))
    
    # Credit details
    credits_amount = Column(Integer, nullable=False)
    price_paid = Column(Numeric(10, 2))  # USD
    
    # Status
    status = Column(String(50), default="completed")  # completed, refunded
    redeemed = Column(Boolean, default=False)
    redeemed_at = Column(DateTime)
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="purchases")


class CreditUsage(Base):
    """
    Track credit usage for analytics and auditing.
    """
    __tablename__ = "credit_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Usage details
    credits_used = Column(Integer, nullable=False)
    tool_name = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="credit_usage")
    
    __table_args__ = (
        Index('idx_credit_usage_user_time', 'user_id', 'created_at'),
    )


# Credit bundles (mapped by Lemon Squeezy variant ID)
# These are loaded from env vars at startup
import os

# Get variant IDs from environment (set on Fly.io)
BASIC_VARIANT = os.getenv("LEMON_BASIC_VARIANT_ID", "1147320")
POWER_VARIANT = os.getenv("LEMON_POWER_VARIANT_ID", "1147340")
PRO_VARIANT = os.getenv("LEMON_PRO_VARIANT_ID", "1147342")

CREDIT_BUNDLES = {
    # variant_id: (credits, price)
    BASIC_VARIANT: (5000, 20),    # $20 = 5,000 credits
    POWER_VARIANT: (12000, 50),   # $50 = 12,000 credits
    PRO_VARIANT: (25000, 100),    # $100 = 25,000 credits
}


# ============================================
# LEGACY SUBSCRIPTION SYSTEM (kept for compatibility)
# ============================================


class Subscription(Base):
    """
    Subscription table - Primary entity for all licensing.
    Maps directly to Lemon Squeezy subscription_id.
    """
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Lemon Squeezy data
    lemon_subscription_id = Column(String(255), unique=True, nullable=False, index=True)
    customer_email = Column(String(255), nullable=False, index=True)
    customer_name = Column(String(255))
    
    # Plan details
    plan = Column(String(50), nullable=False)  # starter|pro|ultra|unlimited
    status = Column(String(50), nullable=False, default="active")  # active|canceled|past_due|expired
    
    # License key (from Lemon Squeezy)
    license_key = Column(String(255), unique=True, index=True)
    
    # Limits
    calls_per_month = Column(Integer, nullable=False, default=500)
    soft_cap_multiplier = Column(Numeric(3, 2), default=Decimal("1.2"))
    hard_cap_multiplier = Column(Numeric(3, 2), default=Decimal("1.5"))
    
    # Dates
    renew_at = Column(DateTime)
    last_refresh_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    license_files = relationship("LicenseFile", back_populates="subscription")
    usage_monthly = relationship("UsageMonthly", back_populates="subscription")
    usage_logs = relationship("UsageLog", back_populates="subscription")
    
    @property
    def soft_limit(self) -> int:
        """Get soft limit (120% of base)"""
        return int(self.calls_per_month * float(self.soft_cap_multiplier))
    
    @property
    def hard_limit(self) -> int:
        """Get hard limit (150% of base)"""
        return int(self.calls_per_month * float(self.hard_cap_multiplier))


class LicenseFile(Base):
    """
    License files - RSA signed license blobs.
    One subscription can have multiple license files (renewals).
    """
    __tablename__ = "license_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    # License content
    license_blob = Column(Text, nullable=False)  # JSON payload
    hash = Column(String(64), nullable=False)     # SHA256 of payload
    signature = Column(Text, nullable=False)       # RSA signature
    
    # Validity
    expires_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="license_files")


class UsageMonthly(Base):
    """
    Monthly usage tracking.
    One row per subscription per month.
    """
    __tablename__ = "usage_monthly"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    month = Column(Date, nullable=False)  # First day of month: 2025-12-01
    calls_used = Column(Integer, default=0)
    overrides_used = Column(Integer, default=0)
    last_warning_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_monthly")
    
    __table_args__ = (
        UniqueConstraint('subscription_id', 'month', name='uq_subscription_month'),
        Index('idx_usage_monthly', 'subscription_id', 'month'),
    )


class UsageLog(Base):
    """
    Individual usage logs for analytics.
    Track each call with feature, tokens, model.
    """
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    
    feature = Column(String(100), nullable=False)  # chat|web_search|memory|agents
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(100))
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_logs")
    
    __table_args__ = (
        Index('idx_usage_logs_sub_time', 'subscription_id', 'timestamp'),
    )

# Plan configurations - Feature progression:
# Free: Chat only
# Starter: Chat + Web Search
# Pro: Starter + Diagrams + Agents
# Ultra: Pro + Memory System
# Unlimited: Ultra + Priority Support
PLAN_LIMITS = {
    "free": {
        "calls_per_month": 50,
        "features": ["chat"]
    },
    "starter": {
        "calls_per_month": 500,
        "features": ["chat", "web_search"]
    },
    "pro": {
        "calls_per_month": 5000,
        "features": ["chat", "web_search", "diagrams", "agents"]
    },
    "ultra": {
        "calls_per_month": 12500,
        "features": ["chat", "web_search", "diagrams", "agents", "memory"]
    },
    "unlimited": {
        "calls_per_month": 50000,
        "features": ["chat", "web_search", "diagrams", "agents", "memory", "priority_support"]
    },
}

# Support email for all plans
SUPPORT_EMAIL = "amariah.abish@gmail.com"
