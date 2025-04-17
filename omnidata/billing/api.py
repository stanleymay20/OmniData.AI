"""
Billing API endpoints for OmniData.AI
"""

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime

from omnidata.billing.models import Plan, Subscription, Invoice, AddOn, UserAddOn
from omnidata.billing.service import BillingService
from omnidata.database import get_db
from omnidata.auth import get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])
security = HTTPBearer()

@router.get("/plans")
async def list_plans(db: Session = Depends(get_db)):
    """List available subscription plans."""
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    return {
        "status": "success",
        "plans": [
            {
                "id": plan.id,
                "name": plan.name,
                "tier": plan.tier,
                "price": plan.price,
                "billing_interval": plan.billing_interval,
                "features": plan.features
            }
            for plan in plans
        ]
    }

@router.post("/subscriptions")
async def create_subscription(
    plan_id: int,
    payment_method_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new subscription."""
    billing_service = BillingService(db)
    result = await billing_service.create_subscription(
        user_id=current_user.id,
        plan_id=plan_id,
        payment_method_id=payment_method_id
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: int,
    at_period_end: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel a subscription."""
    billing_service = BillingService(db)
    result = await billing_service.cancel_subscription(
        subscription_id=subscription_id,
        at_period_end=at_period_end
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/subscriptions/current")
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"])
    ).first()
    
    if not subscription:
        return {"status": "success", "subscription": None}
    
    return {
        "status": "success",
        "subscription": {
            "id": subscription.id,
            "plan_id": subscription.plan_id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end.isoformat(),
            "cancel_at_period_end": subscription.cancel_at_period_end
        }
    }

@router.get("/addons")
async def list_addons(db: Session = Depends(get_db)):
    """List available add-ons."""
    addons = db.query(AddOn).filter(AddOn.is_active == True).all()
    return {
        "status": "success",
        "addons": [
            {
                "id": addon.id,
                "name": addon.name,
                "description": addon.description,
                "type": addon.type,
                "price": addon.price,
                "is_recurring": addon.is_recurring,
                "features": addon.features
            }
            for addon in addons
        ]
    }

@router.post("/addons/{addon_id}/purchase")
async def purchase_addon(
    addon_id: int,
    payment_method_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Purchase an add-on."""
    billing_service = BillingService(db)
    result = await billing_service.purchase_addon(
        user_id=current_user.id,
        addon_id=addon_id,
        payment_method_id=payment_method_id
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.get("/invoices")
async def list_invoices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List user's invoices."""
    invoices = db.query(Invoice).join(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    
    return {
        "status": "success",
        "invoices": [
            {
                "id": invoice.id,
                "amount": invoice.amount,
                "currency": invoice.currency,
                "status": invoice.status,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "created_at": invoice.created_at.isoformat()
            }
            for invoice in invoices
        ]
    }

@router.get("/usage")
async def get_usage(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get usage metrics."""
    billing_service = BillingService(db)
    result = await billing_service.get_usage_metrics(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/webhook")
async def stripe_webhook(
    event_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events."""
    billing_service = BillingService(db)
    result = await billing_service.process_webhook(event_data)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result 