"""
Pydantic Schemas - Request/Response Models
==========================================
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ═══════════════════════════════════════════════════════════
# LICENSE SCHEMAS
# ═══════════════════════════════════════════════════════════

class LicenseValidateRequest(BaseModel):
    """Request to validate/exchange a license key for license.ssx"""
    license_key: str = Field(..., description="Lemon Squeezy license key")
    machine_id: str = Field(..., description="SHA256 hash of machine identifier")


class LicenseLimits(BaseModel):
    """License usage limits"""
    calls_per_month: int = 500
    soft_cap_multiplier: float = 1.2
    hard_cap_multiplier: float = 1.5
    resets_on: str = "monthly"


class LicensePayload(BaseModel):
    """License file JSON payload (before signing)"""
    sub_id: str
    plan: str
    edition: str = "pro"  # starter|pro|ultra|unlimited|enterprise|custom
    user: str
    issued: str
    expires: str
    grace_until: str
    limits: LicenseLimits
    features: List[str]
    machine_id: str
    version: str = "1.0"
    hash: Optional[str] = None  # SHA256 of payload (added after creation)


class LicenseFile(BaseModel):
    """Complete license file with signature"""
    payload: LicensePayload
    signature: str


class LicenseValidateResponse(BaseModel):
    """Response from license validation"""
    valid: bool
    status: str  # active|expired|canceled|invalid
    license_file: Optional[str] = None  # Base64 encoded license.ssx
    message: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# WEBHOOK SCHEMAS (Lemon Squeezy)
# ═══════════════════════════════════════════════════════════

class LemonSqueezyCustomer(BaseModel):
    """Customer data from Lemon Squeezy"""
    email: EmailStr
    name: Optional[str] = None


class LemonSqueezySubscription(BaseModel):
    """Subscription data from webhook"""
    id: str
    customer_id: str
    variant_id: str
    status: str
    renews_at: Optional[datetime] = None


class LemonSqueezyLicenseKey(BaseModel):
    """License key data from webhook"""
    id: str
    key: str
    status: str


class WebhookPayload(BaseModel):
    """Generic Lemon Squeezy webhook payload"""
    meta: dict
    data: dict


# ═══════════════════════════════════════════════════════════
# USAGE SCHEMAS
# ═══════════════════════════════════════════════════════════

class UsageRecord(BaseModel):
    """Single usage record"""
    feature: str
    tokens_used: int = 0
    model_used: Optional[str] = None
    timestamp: datetime


class UsageMonthlyStats(BaseModel):
    """Monthly usage statistics"""
    month: date
    calls_used: int
    calls_limit: int
    soft_limit: int
    hard_limit: int
    percentage_used: float
    overrides_used: int
    overrides_remaining: int = 5


class UsageDetailedResponse(BaseModel):
    """Detailed usage breakdown"""
    subscription_id: str
    plan: str
    status: str
    monthly: UsageMonthlyStats
    by_feature: dict[str, int]
    peak_day: Optional[date] = None
    peak_day_calls: int = 0
    avg_daily: float = 0


# ═══════════════════════════════════════════════════════════
# STATUS SCHEMAS
# ═══════════════════════════════════════════════════════════

class SubscriptionStatus(BaseModel):
    """Full subscription status for CLI display"""
    plan: str
    status: str
    email: str
    expires: datetime
    days_remaining: int
    
    # Usage
    calls_used: int
    calls_limit: int
    soft_limit: int
    percentage_used: float
    
    # Features
    features: List[str]
    
    # Machine
    machine_id: str
    machines_registered: int = 1


# ═══════════════════════════════════════════════════════════
# ERROR SCHEMAS
# ═══════════════════════════════════════════════════════════

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    code: str
    details: Optional[dict] = None
