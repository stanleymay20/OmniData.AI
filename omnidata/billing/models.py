"""
Billing and subscription models for OmniData.AI
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from omnidata.database import Base

class PlanTier(str, Enum):
    """Subscription plan tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Plan(Base):
    """Subscription plan model."""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    tier = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    billing_interval = Column(String(20), default="month")  # month or year
    features = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    @property
    def limits(self) -> Dict[str, Any]:
        """Get plan limits."""
        return {
            "users": self.features.get("max_users", 1),
            "ai_requests": self.features.get("ai_requests_per_month", 100),
            "domains": self.features.get("max_domains", 1),
            "storage_gb": self.features.get("storage_gb", 5),
            "model_deployments": self.features.get("model_deployments", 0)
        }

class Subscription(Base):
    """User subscription model."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    stripe_subscription_id = Column(String(100), unique=True)
    status = Column(String(20), default="active")
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription")

class Invoice(Base):
    """Invoice model for billing."""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    stripe_invoice_id = Column(String(100), unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")

class Usage(Base):
    """Track resource usage for billing."""
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # ai_tokens, storage, compute, etc.
    quantity = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage")

class AddOn(Base):
    """Add-on products and services."""
    __tablename__ = "addons"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50))  # model_pack, dashboard_pack, service, etc.
    price = Column(Float, nullable=False)
    is_recurring = Column(Boolean, default=False)
    billing_interval = Column(String(20), nullable=True)  # month, year, or null for one-time
    features = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAddOn(Base):
    """Track user add-on purchases."""
    __tablename__ = "user_addons"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    addon_id = Column(Integer, ForeignKey("addons.id"), nullable=False)
    stripe_payment_id = Column(String(100))
    status = Column(String(20), default="active")
    purchased_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="addons")
    addon = relationship("AddOn")

class MarketplaceItem(Base):
    """Items available in the marketplace."""
    __tablename__ = "marketplace_items"

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50))  # model, dashboard, config, extension
    price = Column(Float, nullable=False)
    is_approved = Column(Boolean, default=False)
    approval_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seller = relationship("User", back_populates="marketplace_items")
    purchases = relationship("MarketplacePurchase", back_populates="item") 