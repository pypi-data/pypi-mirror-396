"""
StackSense Backend - FastAPI Main Application
==============================================
Fly.io deployment-ready FastAPI backend for license management.
"""

import os
from datetime import datetime, date
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Subscription, LicenseFile, UsageMonthly, PLAN_LIMITS
from schemas import (
    LicenseValidateRequest, LicenseValidateResponse,
    UsageDetailedResponse, UsageMonthlyStats,
    SubscriptionStatus, ErrorResponse
)
from license_signer import LicenseSigner
from webhooks import router as webhook_router

# ═══════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════

app = FastAPI(
    title="StackSense API",
    description="License management and subscription API for StackSense",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router
app.include_router(webhook_router)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════

@app.get("/")
async def health_check():
    """Health check endpoint for Fly.io."""
    return {
        "status": "healthy",
        "service": "stacksense-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {"status": "ok", "database": "connected"}


@app.get("/health/live")
async def health_live():
    """Liveness probe for Kubernetes/Fly.io."""
    return {"status": "live"}


@app.get("/health/ready")
async def health_ready(db: Session = Depends(get_db)):
    """Readiness probe - checks database connection."""
    try:
        # Quick DB check
        db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Not ready: {e}")


# ═══════════════════════════════════════════════════════════
# CREDIT-BASED SYSTEM (One-Time Purchases)
# ═══════════════════════════════════════════════════════════

from models import User, CreditPurchase, CreditUsage, CREDIT_BUNDLES
from pydantic import BaseModel, EmailStr
import httpx


class RedeemRequest(BaseModel):
    """Request to redeem a license key."""
    license_key: str
    device_id: str
    local_credits_used: int = 0  # Credits already used locally (for free tier sync)


class RedeemResponse(BaseModel):
    """Response from redeem endpoint."""
    success: bool
    message: str
    email: str = ""
    credits: int = 0
    total_credits: int = 0
    token: str = ""


class AuthLoginRequest(BaseModel):
    """Login with email + last order ID."""
    email: str
    order_id: str


class AuthResponse(BaseModel):
    """Auth response with token."""
    success: bool
    message: str
    token: str = ""
    credits: int = 0
    email: str = ""


class CreditsBalanceResponse(BaseModel):
    """Credits balance response."""
    email: str
    credits_balance: int
    credits_purchased: int
    credits_used: int
    is_free_tier: bool


class UseCreditsRequest(BaseModel):
    """Request to use credits."""
    amount: int
    tool_name: str


@app.post("/redeem", response_model=RedeemResponse)
async def redeem_license_key(
    request: RedeemRequest,
    db: Session = Depends(get_db)
):
    """
    Redeem a Lemon Squeezy license key for credits.
    
    Flow:
    1. Validate key with Lemon Squeezy API
    2. Check if already redeemed
    3. Create/update user account
    4. Add credits
    5. Return success with auth token
    """
    key = request.license_key.strip()
    
    # Check if already redeemed
    existing = db.query(CreditPurchase).filter(
        CreditPurchase.order_id == key
    ).first()
    
    if existing and existing.redeemed:
        return RedeemResponse(
            success=False,
            message="This key has already been redeemed"
        )
    
    # Validate with Lemon Squeezy API
    lemon_api_key = os.getenv("LEMONSQUEEZY_API_KEY", "")
    
    try:
        # Call Lemon Squeezy to validate the license key
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.lemonsqueezy.com/v1/licenses/validate",
                json={"license_key": key},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {lemon_api_key}"
                },
                timeout=15.0
            )
            
            if response.status_code != 200:
                return RedeemResponse(
                    success=False,
                    message="Invalid license key"
                )
            
            data = response.json()
            
            if not data.get("valid"):
                return RedeemResponse(
                    success=False,
                    message=data.get("error", "License validation failed")
                )
            
            # Extract info from Lemon Squeezy response
            license_data = data.get("license_key", {})
            meta = data.get("meta", {})
            
            customer_email = license_data.get("user_email", meta.get("customer_email", ""))
            customer_name = license_data.get("user_name", meta.get("customer_name", ""))
            variant_id = str(license_data.get("variant_id", ""))
            product_name = license_data.get("product_name", "Credit Bundle")
            order_id = license_data.get("order_id", key)
            
            # Debug logging
            print(f"[REDEEM] license_data keys: {list(license_data.keys())}")
            print(f"[REDEEM] order_id from API: {order_id}, variant_id: '{variant_id}'")
            print(f"[REDEEM] customer_email: {customer_email}")
            
    except httpx.TimeoutException:
        return RedeemResponse(
            success=False,
            message="Lemon Squeezy API timeout. Please try again."
        )
    except Exception as e:
        # In development, allow bypass
        if os.getenv("ENVIRONMENT") == "development":
            customer_email = "test@example.com"
            variant_id = "basic"
            product_name = "Test Bundle"
            order_id = key
        else:
            return RedeemResponse(
                success=False,
                message=f"Validation error: {str(e)}"
            )
    
    # Determine credits to add
    credits_to_add = 0
    
    # Look up unredeemed CreditPurchase by customer email (most recent first)
    # The webhook saves purchases with the correct credits when order is created
    user = db.query(User).filter(User.email == customer_email.lower().strip()).first()
    
    purchase_record = None
    if user:
        purchase_record = db.query(CreditPurchase).filter(
            CreditPurchase.user_id == user.id,
            CreditPurchase.redeemed == False
        ).order_by(CreditPurchase.created_at.desc()).first()
    
    # FIRST: Check if webhook already created a CreditPurchase record with the credits
    # This is the most reliable source since webhook receives variant_id correctly
    if purchase_record and purchase_record.credits_amount and purchase_record.credits_amount > 0:
        credits_to_add = purchase_record.credits_amount
        print(f"[CREDITS] Using credits from webhook record: {credits_to_add} for email {customer_email}")
    else:
        # FALLBACK: Try to determine from variant_id (rarely works since Lemon Squeezy license API doesn't return it)
        basic_var = os.getenv("LEMON_BASIC_VARIANT_ID", "").strip('"').strip("'")
        power_var = os.getenv("LEMON_POWER_VARIANT_ID", "").strip('"').strip("'")
        pro_var = os.getenv("LEMON_PRO_VARIANT_ID", "").strip('"').strip("'")
        
        variant_id_clean = str(variant_id).strip('"').strip("'")
        
        if variant_id_clean == pro_var:
            credits_to_add = 25000
        elif variant_id_clean == power_var:
            credits_to_add = 12000
        elif variant_id_clean == basic_var:
            credits_to_add = 5000
        else:
            # Fallback to CREDIT_BUNDLES dict
            bundle_info = CREDIT_BUNDLES.get(variant_id_clean)
            if bundle_info:
                credits_to_add = bundle_info[0]
            else:
                print(f"[CREDITS] Unknown variant_id: '{variant_id_clean}', no webhook record, defaulting to 5000")
                credits_to_add = 5000
    
    # Get or create user
    user = db.query(User).filter(User.email == customer_email).first()
    
    if not user:
        # New user: Start with 250 free credits, subtract any already used locally
        initial_balance = max(0, 250 - request.local_credits_used)
        user = User(
            email=customer_email,
            name=customer_name,
            credits_balance=initial_balance,
            credits_total_used=request.local_credits_used,  # Track usage from free tier
            is_free_tier=True
        )
        db.add(user)
        db.flush()
    
    # Add credits
    user.credits_balance += credits_to_add
    user.credits_total_purchased += credits_to_add
    user.is_free_tier = False
    user.last_order_id = order_id
    user.generate_auth_token()
    
    # Record purchase
    purchase = CreditPurchase(
        user_id=user.id,
        order_id=order_id,
        variant_id=variant_id,
        product_name=product_name,
        credits_amount=credits_to_add,
        redeemed=True,
        redeemed_at=datetime.utcnow()
    )
    db.add(purchase)
    db.commit()
    
    return RedeemResponse(
        success=True,
        message=f"Successfully redeemed {credits_to_add:,} credits!",
        email=customer_email,
        credits=credits_to_add,
        total_credits=user.credits_balance,
        token=user.auth_token
    )


@app.post("/auth/login", response_model=AuthResponse)
async def auth_login(
    request: AuthLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email + last order ID (no password needed).
    Returns auth token for API access.
    """
    user = db.query(User).filter(
        User.email == request.email.lower().strip()
    ).first()
    
    if not user:
        return AuthResponse(
            success=False,
            message="No account found with this email. Purchase credits first."
        )
    
    # Verify order ID matches
    if user.last_order_id != request.order_id.strip():
        return AuthResponse(
            success=False,
            message="Order ID does not match. Use your most recent order."
        )
    
    # Generate new auth token
    user.generate_auth_token()
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return AuthResponse(
        success=True,
        message="Login successful",
        token=user.auth_token,
        credits=user.credits_balance,
        email=user.email
    )


@app.get("/auth/verify")
async def auth_verify(
    x_auth_token: str = Header(..., alias="X-Auth-Token"),
    db: Session = Depends(get_db)
):
    """Verify auth token is valid."""
    user = db.query(User).filter(User.auth_token == x_auth_token).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    return {
        "valid": True,
        "email": user.email,
        "credits": user.credits_balance
    }


@app.get("/credits/balance", response_model=CreditsBalanceResponse)
async def get_credits_balance(
    x_auth_token: str = Header(..., alias="X-Auth-Token"),
    db: Session = Depends(get_db)
):
    """Get current credit balance (server is authoritative)."""
    user = db.query(User).filter(User.auth_token == x_auth_token).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    user.last_sync_at = datetime.utcnow()
    db.commit()
    
    return CreditsBalanceResponse(
        email=user.email,
        credits_balance=user.credits_balance,
        credits_purchased=user.credits_total_purchased,
        credits_used=user.credits_total_used,
        is_free_tier=user.is_free_tier
    )


class CreditsSyncRequest(BaseModel):
    """Request to sync local credits with server."""
    email: str
    device_id: str
    credits_used: int  # Total credits used locally


class CreditsSyncResponse(BaseModel):
    """Response from credits sync."""
    success: bool
    credits_total: int  # Server's authoritative total
    credits_used: int   # Server's authoritative used
    credits_remaining: int


@app.post("/credits/sync", response_model=CreditsSyncResponse)
async def sync_credits(
    request: CreditsSyncRequest,
    db: Session = Depends(get_db)
):
    """
    Sync local credits with server (called every 100 credits or 24 hours).
    
    Server is authoritative:
    - Accepts local usage and updates server-side total_used
    - Returns current balance for local storage to update
    """
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()
    
    if not user:
        # User not in server DB yet (free tier only, never purchased)
        # Return a "fake" sync that mirrors what local has
        return CreditsSyncResponse(
            success=True,
            credits_total=250,
            credits_used=request.credits_used,
            credits_remaining=max(0, 250 - request.credits_used)
        )
    
    # Update server's usage tracking with local data
    # Take the max to never lose usage history
    if request.credits_used > user.credits_total_used:
        user.credits_total_used = request.credits_used
        user.credits_balance = max(0, user.credits_total_purchased + 250 - request.credits_used)
    
    user.last_sync_at = datetime.utcnow()
    db.commit()
    
    return CreditsSyncResponse(
        success=True,
        credits_total=user.credits_total_purchased + 250,  # All purchased + free tier
        credits_used=user.credits_total_used,
        credits_remaining=user.credits_balance
    )


@app.post("/credits/use")
async def use_credits(
    request: UseCreditsRequest,
    x_auth_token: str = Header(..., alias="X-Auth-Token"),
    db: Session = Depends(get_db)
):
    """
    Use credits for a tool call (server-side tracking).
    Returns updated balance and whether call was allowed.
    """
    user = db.query(User).filter(User.auth_token == x_auth_token).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    # Check if enough credits
    if user.credits_balance < request.amount:
        return {
            "success": False,
            "message": f"Insufficient credits. Need {request.amount}, have {user.credits_balance}",
            "credits_remaining": user.credits_balance,
            "purchase_url": os.getenv("LEMON_BASIC_CHECKOUT_URL", "")
        }
    
    # Deduct credits
    user.credits_balance -= request.amount
    user.credits_total_used += request.amount
    
    # Log usage
    usage = CreditUsage(
        user_id=user.id,
        credits_used=request.amount,
        tool_name=request.tool_name
    )
    db.add(usage)
    db.commit()
    
    return {
        "success": True,
        "credits_used": request.amount,
        "credits_remaining": user.credits_balance,
        "tool": request.tool_name
    }


@app.get("/credits/bundles")
async def get_credit_bundles(email: str = None):
    """
    Get available credit bundles with dynamically generated checkout URLs.
    
    Args:
        email: Optional customer email to pre-fill checkout
    """
    store_id = os.getenv("LEMONSQUEEZY_STORE_ID", "").strip('"')
    api_key = os.getenv("LEMONSQUEEZY_API_KEY", "").strip('"')
    
    bundles_config = [
        {
            "name": "Basic",
            "credits": 5000,
            "price": 20,
            "price_per_credit": 0.004,
            "variant_id": os.getenv("LEMON_BASIC_VARIANT_ID", "").strip('"')
        },
        {
            "name": "Power",
            "credits": 12000,
            "price": 50,
            "price_per_credit": 0.0042,
            "recommended": True,
            "variant_id": os.getenv("LEMON_POWER_VARIANT_ID", "").strip('"')
        },
        {
            "name": "Pro Stack",
            "credits": 25000,
            "price": 100,
            "price_per_credit": 0.004,
            "variant_id": os.getenv("LEMON_PRO_VARIANT_ID", "").strip('"')
        }
    ]
    
    bundles = []
    
    for bundle in bundles_config:
        checkout_url = ""
        
        # Generate dynamic checkout URL if API key is available
        if api_key and store_id and bundle["variant_id"]:
            try:
                checkout_data = {
                    "data": {
                        "type": "checkouts",
                        "attributes": {},
                        "relationships": {
                            "store": {
                                "data": {
                                    "type": "stores",
                                    "id": store_id
                                }
                            },
                            "variant": {
                                "data": {
                                    "type": "variants",
                                    "id": bundle["variant_id"]
                                }
                            }
                        }
                    }
                }
                
                # Pre-fill email if provided
                if email:
                    checkout_data["data"]["attributes"]["checkout_data"] = {
                        "email": email
                    }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.lemonsqueezy.com/v1/checkouts",
                        json=checkout_data,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Accept": "application/vnd.api+json",
                            "Content-Type": "application/vnd.api+json"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 201:
                        data = response.json()
                        checkout_url = data.get("data", {}).get("attributes", {}).get("url", "")
            except Exception as e:
                # Fallback to static URL if API fails
                checkout_url = os.getenv(f"LEMON_{bundle['name'].upper()}_CHECKOUT_URL", "")
        
        bundles.append({
            "name": bundle["name"],
            "credits": bundle["credits"],
            "price": bundle["price"],
            "price_per_credit": bundle["price_per_credit"],
            "recommended": bundle.get("recommended", False),
            "url": checkout_url
        })
    
    return {
        "bundles": bundles,
        "free_credits": 250
    }


# ═══════════════════════════════════════════════════════════
# LICENSE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.post("/license/validate", response_model=LicenseValidateResponse)
async def validate_license(
    request: LicenseValidateRequest,
    db: Session = Depends(get_db)
):
    """
    Validate license key and return signed license file.
    
    This is the key exchange endpoint:
    - User provides license_key once
    - Backend returns signed license.ssx
    - CLI stores locally for offline use
    """
    # Find subscription by license key
    subscription = db.query(Subscription).filter(
        Subscription.license_key == request.license_key
    ).first()
    
    if not subscription:
        return LicenseValidateResponse(
            valid=False,
            status="invalid",
            message="License key not found"
        )
    
    # Check subscription status
    if subscription.status == "expired":
        return LicenseValidateResponse(
            valid=False,
            status="expired",
            message="Subscription has expired. Please renew at stacksense.dev/upgrade"
        )
    
    if subscription.status == "canceled":
        return LicenseValidateResponse(
            valid=False,
            status="canceled",
            message="Subscription was canceled. Reactivate at stacksense.dev/upgrade"
        )
    
    # Generate fresh license file
    try:
        signer = LicenseSigner()
        license_json, hash_val, signature = signer.create_license_file(
            subscription_id=subscription.lemon_subscription_id,
            plan=subscription.plan,
            email=subscription.customer_email,
            machine_id=request.machine_id,
            validity_days=30
        )
        
        # Store in database
        import base64
        license_record = LicenseFile(
            subscription_id=subscription.id,
            license_blob=license_json,
            hash=hash_val,
            signature=signature,
            expires_at=datetime.utcnow().replace(day=1) + timedelta(days=60)
        )
        db.add(license_record)
        
        # Update last refresh
        subscription.last_refresh_at = datetime.utcnow()
        db.commit()
        
        # Return base64 encoded license
        license_b64 = base64.b64encode(license_json.encode()).decode()
        
        return LicenseValidateResponse(
            valid=True,
            status="active",
            license_file=license_b64,
            message=f"License valid for {subscription.plan} plan"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"License generation failed: {str(e)}")


@app.get("/license/refresh")
async def refresh_license(
    license_key: str = Header(..., alias="X-License-Key"),
    machine_id: str = Header(..., alias="X-Machine-ID"),
    db: Session = Depends(get_db)
):
    """
    Refresh an existing license (weekly/monthly check).
    Same as validate but for existing users.
    """
    request = LicenseValidateRequest(
        license_key=license_key,
        machine_id=machine_id
    )
    return await validate_license(request, db)


# ═══════════════════════════════════════════════════════════
# USAGE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/usage/{subscription_id}", response_model=UsageDetailedResponse)
async def get_usage(
    subscription_id: str,
    license_key: str = Header(..., alias="X-License-Key"),
    db: Session = Depends(get_db)
):
    """Get detailed usage statistics for a subscription."""
    # Verify license key matches subscription
    subscription = db.query(Subscription).filter(
        Subscription.lemon_subscription_id == subscription_id,
        Subscription.license_key == license_key
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get current month's usage
    today = date.today()
    first_of_month = today.replace(day=1)
    
    usage = db.query(UsageMonthly).filter(
        UsageMonthly.subscription_id == subscription.id,
        UsageMonthly.month == first_of_month
    ).first()
    
    calls_used = usage.calls_used if usage else 0
    
    # Calculate stats
    monthly_stats = UsageMonthlyStats(
        month=first_of_month,
        calls_used=calls_used,
        calls_limit=subscription.calls_per_month,
        soft_limit=subscription.soft_limit,
        hard_limit=subscription.hard_limit,
        percentage_used=(calls_used / subscription.calls_per_month * 100) if subscription.calls_per_month > 0 else 0,
        overrides_used=usage.overrides_used if usage else 0,
        overrides_remaining=5 - (usage.overrides_used if usage else 0)
    )
    
    return UsageDetailedResponse(
        subscription_id=subscription_id,
        plan=subscription.plan,
        status=subscription.status,
        monthly=monthly_stats,
        by_feature={},  # TODO: Aggregate from usage_logs
        avg_daily=calls_used / max(today.day, 1)
    )


@app.post("/usage/record")
async def record_usage(
    feature: str,
    tokens: int = 0,
    model: Optional[str] = None,
    license_key: str = Header(..., alias="X-License-Key"),
    db: Session = Depends(get_db)
):
    """
    Record a usage event (called by CLI after each action).
    Returns current usage status and any warnings.
    """
    from models import UsageLog
    
    subscription = db.query(Subscription).filter(
        Subscription.license_key == license_key
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Invalid license")
    
    # Get or create monthly usage
    today = date.today()
    first_of_month = today.replace(day=1)
    
    usage = db.query(UsageMonthly).filter(
        UsageMonthly.subscription_id == subscription.id,
        UsageMonthly.month == first_of_month
    ).first()
    
    if not usage:
        usage = UsageMonthly(
            subscription_id=subscription.id,
            month=first_of_month,
            calls_used=0
        )
        db.add(usage)
    
    # Increment usage
    usage.calls_used += 1
    
    # Log individual call
    log = UsageLog(
        subscription_id=subscription.id,
        feature=feature,
        tokens_used=tokens,
        model_used=model
    )
    db.add(log)
    db.commit()
    
    # Calculate percentage
    limit = subscription.calls_per_month
    used = usage.calls_used
    percentage = (used / limit * 100) if limit > 0 else 0
    
    # Determine warning level
    warning = None
    blocked = False
    
    if percentage >= 150:
        blocked = True
        warning = f"🚫 Hard limit reached ({used}/{limit}). Upgrade: stacksense.dev/upgrade"
    elif percentage >= 120:
        warning = f"🚫 Soft limit reached ({used}/{limit}). Use override or upgrade."
    elif percentage >= 100:
        warning = f"⚠️ Monthly limit exceeded ({used}/{limit}). Grace period active."
    elif percentage >= 80:
        warning = f"⚠️ {int(percentage)}% of monthly limit used ({used}/{limit})"
    
    return {
        "recorded": True,
        "calls_used": used,
        "calls_limit": limit,
        "percentage": percentage,
        "warning": warning,
        "blocked": blocked
    }


# ═══════════════════════════════════════════════════════════
# STATUS ENDPOINT
# ═══════════════════════════════════════════════════════════

@app.get("/status", response_model=SubscriptionStatus)
async def get_status(
    license_key: str = Header(..., alias="X-License-Key"),
    machine_id: str = Header(..., alias="X-Machine-ID"),
    db: Session = Depends(get_db)
):
    """Get full subscription status for CLI display."""
    subscription = db.query(Subscription).filter(
        Subscription.license_key == license_key
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Invalid license")
    
    # Get usage
    today = date.today()
    first_of_month = today.replace(day=1)
    
    usage = db.query(UsageMonthly).filter(
        UsageMonthly.subscription_id == subscription.id,
        UsageMonthly.month == first_of_month
    ).first()
    
    calls_used = usage.calls_used if usage else 0
    
    # Calculate days remaining
    days_remaining = 0
    if subscription.renew_at:
        days_remaining = (subscription.renew_at.date() - today).days
    
    # Get features
    plan_config = PLAN_LIMITS.get(subscription.plan, PLAN_LIMITS["starter"])
    
    return SubscriptionStatus(
        plan=subscription.plan,
        status=subscription.status,
        email=subscription.customer_email,
        expires=subscription.renew_at or datetime.utcnow(),
        days_remaining=max(days_remaining, 0),
        calls_used=calls_used,
        calls_limit=subscription.calls_per_month,
        soft_limit=subscription.soft_limit,
        percentage_used=(calls_used / subscription.calls_per_month * 100) if subscription.calls_per_month > 0 else 0,
        features=plan_config["features"],
        machine_id=machine_id
    )


# ═══════════════════════════════════════════════════════════
# PRICING INFO (Public)
# ═══════════════════════════════════════════════════════════

@app.get("/pricing")
async def get_pricing():
    """Get current pricing tiers (for CLI upgrade command)."""
    return {
        "tiers": [
            {
                "name": "Starter",
                "price": 9,
                "period": "month",
                "calls": 500,
                "features": ["chat", "web_search"],
                "url": os.getenv("LEMON_STARTER_URL", "https://stacksense.lemonsqueezy.com/buy/starter")
            },
            {
                "name": "Pro",
                "price": 29,
                "period": "month",
                "calls": 5000,
                "features": ["chat", "web_search", "memory", "agents"],
                "recommended": True,
                "url": os.getenv("LEMON_PRO_URL", "https://stacksense.lemonsqueezy.com/buy/pro")
            },
            {
                "name": "Ultra",
                "price": 49,
                "period": "month",
                "calls": 12500,
                "features": ["chat", "web_search", "memory", "agents", "marketplace"],
                "url": os.getenv("LEMON_ULTRA_URL", "https://stacksense.lemonsqueezy.com/buy/ultra")
            },
            {
                "name": "Unlimited",
                "price": 99,
                "period": "month",
                "calls": 50000,
                "soft_cap": True,
                "features": ["chat", "web_search", "memory", "agents", "marketplace", "priority"],
                "url": os.getenv("LEMON_UNLIMITED_URL", "https://stacksense.lemonsqueezy.com/buy/unlimited")
            },
            {
                "name": "Enterprise",
                "price": 299,
                "period": "month",
                "calls": -1,  # Unlimited
                "features": [
                    "unlimited_seats", "unlimited_calls", "custom_models",
                    "private_region", "sso", "white_label", "dedicated_support"
                ],
                "contact": "enterprise@stacksense.dev",
                "description": "Unlimited team seats, custom model integrations, SSO, white-label CLI"
            }
        ],
        "free_tier": {
            "calls": 50,
            "period": "day",
            "features": ["chat"]
        }
    }


# Missing import
from datetime import timedelta
