"""
Lemon Squeezy Webhook Handlers
==============================
Handle one-time credit purchases from Lemon Squeezy.
"""

import os
import hmac
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix="/webhook", tags=["webhooks"])

# Lemon Squeezy webhook secret
WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

# Credit bundles mapped to variant IDs
# Update these with your actual Lemon Squeezy variant IDs
CREDIT_BUNDLES = {
    # "variant_id": credits_amount
    os.getenv("LEMON_BASIC_VARIANT_ID", "basic"): 5000,      # $20 = 5,000 credits
    os.getenv("LEMON_POWER_VARIANT_ID", "power"): 12000,     # $50 = 12,000 credits
    os.getenv("LEMON_PRO_VARIANT_ID", "pro"): 25000,         # $100 = 25,000 credits
}


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Lemon Squeezy webhook signature.
    
    Args:
        payload: Raw request body
        signature: X-Signature header value
        
    Returns:
        True if signature is valid
    """
    if not WEBHOOK_SECRET:
        return True  # Skip in development
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


def get_credits_for_variant(variant_id: str) -> int:
    """
    Get credit amount for a Lemon Squeezy variant ID.
    """
    return CREDIT_BUNDLES.get(str(variant_id), 0)


@router.post("/lemonsqueezy")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Lemon Squeezy webhook events for one-time credit purchases.
    
    Events handled:
    - order_created: Customer purchased a credit bundle
    - order_refunded: Customer got a refund (remove credits)
    """
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    
    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_name = payload.get("meta", {}).get("event_name", "")
    data = payload.get("data", {})
    attributes = data.get("attributes", {})
    
    # Route to handler
    handlers = {
        "order_created": handle_order_created,
        "order_refunded": handle_order_refunded,
    }
    
    handler = handlers.get(event_name)
    if handler:
        await handler(data, attributes, db)
    
    return {"status": "ok", "event": event_name}


async def handle_order_created(
    data: dict,
    attributes: dict,
    db: Session
):
    """
    Handle new credit purchase order.
    
    Flow:
    1. Extract customer email and variant ID from order
    2. Look up how many credits this variant gives
    3. Add credits to customer's account (or create account)
    4. Send confirmation (optional)
    """
    order_id = str(data.get("id"))
    
    # Extract customer info
    customer_email = attributes.get("user_email", "")
    customer_name = attributes.get("user_name", "")
    
    # Get the first line item's variant ID
    first_order_item = attributes.get("first_order_item", {})
    variant_id = str(first_order_item.get("variant_id", ""))
    product_name = first_order_item.get("product_name", "Credit Bundle")
    
    # Determine credits to add
    credits_purchased = get_credits_for_variant(variant_id)
    
    if credits_purchased == 0:
        # Unknown variant, log but don't fail
        print(f"[Webhook] Unknown variant ID: {variant_id} for order {order_id}")
        return
    
    # Import models
    from models import User, CreditPurchase
    
    # Get or create user
    user = db.query(User).filter(User.email == customer_email.lower().strip()).first()
    
    if not user:
        # Create new user with free credits
        user = User(
            email=customer_email.lower().strip(),
            name=customer_name,
            credits_balance=250,  # Start with free credits
            is_free_tier=True
        )
        db.add(user)
        db.flush()
    
    # Check if this order was already processed
    existing_purchase = db.query(CreditPurchase).filter(
        CreditPurchase.order_id == order_id
    ).first()
    
    if existing_purchase:
        print(f"[Webhook] Order {order_id} already processed, skipping")
        return
    
    # Add credits to user
    user.credits_balance += credits_purchased
    user.credits_total_purchased += credits_purchased
    user.is_free_tier = False
    user.last_order_id = order_id
    
    # Save purchase record
    purchase = CreditPurchase(
        user_id=user.id,
        order_id=order_id,
        variant_id=variant_id,
        product_name=product_name,
        credits_amount=credits_purchased,
        redeemed=False  # Will be marked True when user runs stacksense redeem
    )
    db.add(purchase)
    db.commit()
    
    print(f"[Webhook] Order {order_id}: {customer_email} purchased {credits_purchased} credits ({product_name})")


async def handle_order_refunded(
    data: dict,
    attributes: dict,
    db: Session
):
    """
    Handle order refund - remove credited credits.
    """
    order_id = str(data.get("id"))
    
    # Extract customer info
    customer_email = attributes.get("user_email", "")
    
    # Get variant to know how many credits to remove
    first_order_item = attributes.get("first_order_item", {})
    variant_id = str(first_order_item.get("variant_id", ""))
    credits_to_remove = get_credits_for_variant(variant_id)
    
    # Import models
    from models import User, CreditPurchase
    
    # Find the purchase record
    purchase = db.query(CreditPurchase).filter(
        CreditPurchase.order_id == order_id
    ).first()
    
    if purchase:
        # Mark purchase as refunded
        purchase.status = "refunded"
        
        # Remove credits from user
        user = purchase.user
        if user:
            user.credits_balance = max(0, user.credits_balance - credits_to_remove)
            user.credits_total_purchased = max(0, user.credits_total_purchased - credits_to_remove)
            
            # If no more purchased credits, reset to free tier
            if user.credits_total_purchased == 0:
                user.is_free_tier = True
                user.credits_balance = max(0, min(250, user.credits_balance))  # Cap at free tier
        
        db.commit()
    
    print(f"[Webhook] Refund {order_id}: Removed {credits_to_remove} credits from {customer_email}")


