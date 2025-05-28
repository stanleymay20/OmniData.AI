from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import stripe
from ..core.auth import get_current_user
from ..core.config import settings

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionTier(BaseModel):
    name: str
    price_id: str
    features: list[str]
    price: float
    scroll_limit: int

SUBSCRIPTION_TIERS = {
    "seeker": SubscriptionTier(
        name="Seeker",
        price_id="price_seeker",
        features=["10 scrolls per day", "Basic insights", "Email support"],
        price=9.99,
        scroll_limit=10
    ),
    "scribe": SubscriptionTier(
        name="Scribe",
        price_id="price_scribe",
        features=["50 scrolls per day", "Advanced insights", "Priority support"],
        price=29.99,
        scroll_limit=50
    ),
    "prophet": SubscriptionTier(
        name="Prophet",
        price_id="price_prophet",
        features=["Unlimited scrolls", "Custom insights", "24/7 support"],
        price=99.99,
        scroll_limit=-1  # Unlimited
    )
}

@router.post("/subscribe")
async def create_subscription(
    tier: str,
    current_user = Depends(get_current_user)
):
    """Create a new subscription"""
    if tier not in SUBSCRIPTION_TIERS:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    try:
        # Create or get Stripe customer
        customer = stripe.Customer.create(
            email=current_user.email,
            metadata={"user_id": current_user.id}
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": SUBSCRIPTION_TIERS[tier].price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event.type == "invoice.paid":
        # Update user's subscription status
        subscription = event.data.object
        customer_id = subscription.customer
        # TODO: Update user's subscription in database
        
    elif event.type == "customer.subscription.deleted":
        # Handle subscription cancellation
        subscription = event.data.object
        customer_id = subscription.customer
        # TODO: Update user's subscription status in database
    
    return {"status": "success"}

@router.get("/billing")
async def get_billing_info(current_user = Depends(get_current_user)):
    """Get current subscription and billing information"""
    try:
        # Get customer's subscriptions
        subscriptions = stripe.Subscription.list(
            customer=current_user.stripe_customer_id,
            limit=1
        )
        
        if not subscriptions.data:
            return {"status": "no_subscription"}
        
        subscription = subscriptions.data[0]
        return {
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "tier": subscription.items.data[0].price.nickname
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cancel")
async def cancel_subscription(current_user = Depends(get_current_user)):
    """Cancel current subscription"""
    try:
        subscriptions = stripe.Subscription.list(
            customer=current_user.stripe_customer_id,
            limit=1
        )
        
        if not subscriptions.data:
            raise HTTPException(status_code=400, detail="No active subscription")
        
        subscription = subscriptions.data[0]
        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True
        )
        
        return {"status": "success", "message": "Subscription will be canceled at the end of the billing period"}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e)) 