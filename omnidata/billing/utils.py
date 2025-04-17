"""
Billing utility functions for OmniData.AI
"""

from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

def calculate_prorated_amount(
    base_amount: float,
    start_date: datetime,
    end_date: datetime,
    billing_interval: str = "month"
) -> float:
    """Calculate prorated amount for partial billing period."""
    if end_date < start_date:
        raise ValueError("End date must be after start date")
    
    # Convert to Decimal for precise calculations
    base = Decimal(str(base_amount))
    
    # Calculate total days in billing interval
    if billing_interval == "month":
        total_days = Decimal('30')  # Standard month
    elif billing_interval == "year":
        total_days = Decimal('365')
    else:
        raise ValueError("Invalid billing interval")
    
    # Calculate actual days
    actual_days = Decimal(str((end_date - start_date).days))
    
    # Calculate prorated amount
    prorated = (base * actual_days / total_days).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    return float(prorated)

def calculate_usage_cost(
    usage_quantity: float,
    plan_limits: Dict[str, Any],
    resource_type: str
) -> Tuple[float, bool]:
    """Calculate cost for usage-based resources."""
    if usage_quantity < 0:
        raise ValueError("Usage quantity cannot be negative")
    
    included_key = f"{resource_type}_included"
    if included_key not in plan_limits:
        raise ValueError(f"No limit defined for {resource_type}")
    
    included_quantity = plan_limits[included_key]
    within_limits = usage_quantity <= included_quantity
    
    if within_limits:
        return 0.0, True
    
    # Calculate overage
    overage = usage_quantity - included_quantity
    rate_key = f"{resource_type}_overage_rate"
    rate = plan_limits.get(rate_key, 0.01)  # Default rate $0.01 per unit
    
    cost = Decimal(str(overage)) * Decimal(str(rate))
    return float(cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)), False

def get_plan_features(tier: str) -> Dict[str, Any]:
    """Get features and limits for a subscription tier."""
    features = {
        "free": {
            "ai_requests_included": 100,
            "storage_gb": 5,
            "domains": 1,
            "support_level": "community"
        },
        "pro": {
            "ai_requests_included": 10000,
            "storage_gb": 50,
            "domains": 5,
            "support_level": "priority"
        },
        "enterprise": {
            "ai_requests_included": float('inf'),
            "storage_gb": float('inf'),
            "domains": float('inf'),
            "support_level": "dedicated"
        }
    }
    
    if tier not in features:
        raise ValueError(f"Invalid plan tier: {tier}")
    
    return features[tier]

def calculate_marketplace_commission(
    sale_amount: float,
    commission_rate: float = 0.15
) -> float:
    """Calculate marketplace commission."""
    if sale_amount < 0:
        raise ValueError("Sale amount cannot be negative")
    if not 0 <= commission_rate <= 1:
        raise ValueError("Commission rate must be between 0 and 1")
    
    commission = Decimal(str(sale_amount)) * Decimal(str(commission_rate))
    return float(commission.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def validate_addon_price(price: float, addon_type: str) -> bool:
    """Validate add-on price against minimum requirements."""
    min_prices = {
        "model_pack": 499,
        "dashboard_pack": 299,
        "finetuning": 1500,
        "consulting": 250
    }
    
    if addon_type not in min_prices:
        raise ValueError(f"Invalid add-on type: {addon_type}")
    
    return price >= min_prices[addon_type]

def calculate_subscription_metrics(
    subscriptions: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Calculate subscription metrics for a period."""
    if end_date < start_date:
        raise ValueError("End date must be after start date")
    
    total_mrr = Decimal('0')
    active_count = 0
    churned_count = 0
    
    for sub in subscriptions:
        if sub["status"] not in ["active", "canceled", "churned"]:
            continue
            
        if start_date <= sub["updated_at"] <= end_date:
            if sub["status"] == "active":
                total_mrr += Decimal(str(sub["amount"]))
                active_count += 1
            elif sub["status"] in ["canceled", "churned"]:
                churned_count += 1
    
    churn_rate = (churned_count / active_count) if active_count > 0 else 0
    
    return {
        "mrr": float(total_mrr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        "active_subscriptions": active_count,
        "churned_subscriptions": churned_count,
        "churn_rate": round(churn_rate * 100, 2)
    }

def format_invoice_line_items(
    items: List[Dict[str, Any]],
    currency: str = "USD"
) -> List[Dict[str, Any]]:
    """Format invoice line items for display."""
    formatted_items = []
    total = Decimal('0')
    
    for item in items:
        if "amount" not in item or "description" not in item:
            raise ValueError("Invalid line item format")
        
        amount = Decimal(str(item["amount"]))
        total += amount
        
        formatted_items.append({
            "description": item["description"],
            "amount": f"{currency} {amount:.2f}",
            "quantity": item.get("quantity", 1),
            "subtotal": f"{currency} {(amount * Decimal(str(item.get('quantity', 1)))):.2f}"
        })
    
    return {
        "items": formatted_items,
        "total": f"{currency} {total:.2f}"
    }

def check_resource_limits(
    current_usage: Dict[str, float],
    plan_limits: Dict[str, float]
) -> Dict[str, Dict[str, bool]]:
    """Check if current usage is within plan limits."""
    if not current_usage or not plan_limits:
        raise ValueError("Usage and limits must not be empty")
    
    status = {}
    for resource, usage in current_usage.items():
        if usage < 0:
            raise ValueError(f"Usage for {resource} cannot be negative")
        
        if resource not in plan_limits:
            raise ValueError(f"No limit defined for {resource}")
        
        limit = plan_limits[resource]
        status[resource] = {
            "within_limit": usage <= limit,
            "usage": usage,
            "limit": limit,
            "usage_percentage": round((usage / limit * 100) if limit > 0 else 100, 2)
        }
    
    return status 