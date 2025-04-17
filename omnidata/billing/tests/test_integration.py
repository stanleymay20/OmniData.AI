"""
Integration tests for billing system.
"""

import unittest
from datetime import datetime, timedelta
import os
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from omnidata.database import Base
from omnidata.billing.models import Plan, Subscription, Invoice, Usage, AddOn, UserAddOn
from omnidata.billing.service import BillingService
from omnidata.billing.utils import (
    calculate_prorated_amount,
    calculate_usage_cost,
    get_plan_features
)

class TestBillingIntegration(unittest.TestCase):
    """Integration tests for billing system."""

    @classmethod
    def setUpClass(cls):
        """Set up test database and service."""
        # Create test database
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        Session = sessionmaker(bind=cls.engine)
        cls.session = Session()

        # Initialize billing service
        cls.billing_service = BillingService(cls.session)

        # Set up test data
        cls._create_test_plans()

    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.session.close()
        Base.metadata.drop_all(cls.engine)

    @classmethod
    def _create_test_plans(cls):
        """Create test subscription plans."""
        plans = [
            Plan(
                name="Free",
                tier="free",
                price=0.00,
                features={
                    "ai_requests": 100,
                    "storage_gb": 5,
                    "domains": 1
                }
            ),
            Plan(
                name="Pro",
                tier="pro",
                price=99.00,
                features={
                    "ai_requests": 10000,
                    "storage_gb": 50,
                    "domains": 5
                }
            ),
            Plan(
                name="Enterprise",
                tier="enterprise",
                price=999.00,
                features={
                    "ai_requests": float('inf'),
                    "storage_gb": float('inf'),
                    "domains": float('inf')
                }
            )
        ]
        
        for plan in plans:
            cls.session.add(plan)
        cls.session.commit()

    def test_subscription_lifecycle(self):
        """Test complete subscription lifecycle."""
        # Create customer
        customer_result = self.billing_service.create_customer(
            user_id=1,
            email="test@example.com"
        )
        self.assertEqual(customer_result["status"], "success")

        # Create subscription
        subscription_result = self.billing_service.create_subscription(
            user_id=1,
            plan_id=2,  # Pro plan
            payment_method_id="pm_test_card"
        )
        self.assertEqual(subscription_result["status"], "success")
        subscription_id = subscription_result["subscription_id"]

        # Track usage
        usage_result = self.billing_service.track_usage(
            user_id=1,
            resource_type="ai_requests",
            quantity=500
        )
        self.assertEqual(usage_result["status"], "success")

        # Get usage metrics
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        metrics_result = self.billing_service.get_usage_metrics(
            user_id=1,
            start_date=start_date,
            end_date=end_date
        )
        self.assertEqual(metrics_result["status"], "success")
        self.assertEqual(metrics_result["metrics"]["ai_requests"]["total"], 500)

        # Cancel subscription
        cancel_result = self.billing_service.cancel_subscription(
            subscription_id=subscription_id,
            at_period_end=True
        )
        self.assertEqual(cancel_result["status"], "success")

    def test_addon_purchase_flow(self):
        """Test add-on purchase process."""
        # Create add-on
        addon = AddOn(
            name="Model Pack",
            description="Premium model package",
            type="model_pack",
            price=499.00,
            features={"models": ["gpt-4", "claude-v2"]}
        )
        self.session.add(addon)
        self.session.commit()

        # Purchase add-on
        purchase_result = self.billing_service.purchase_addon(
            user_id=1,
            addon_id=addon.id,
            payment_method_id="pm_test_card"
        )
        self.assertEqual(purchase_result["status"], "success")

        # Verify purchase
        user_addon = self.session.query(UserAddOn).filter_by(
            user_id=1,
            addon_id=addon.id
        ).first()
        self.assertIsNotNone(user_addon)
        self.assertEqual(user_addon.status, "active")

    def test_usage_tracking_and_billing(self):
        """Test usage tracking and billing cycle."""
        # Create subscription
        subscription_result = self.billing_service.create_subscription(
            user_id=1,
            plan_id=2,  # Pro plan
            payment_method_id="pm_test_card"
        )
        subscription_id = subscription_result["subscription_id"]

        # Track usage over limit
        usage_result = self.billing_service.track_usage(
            user_id=1,
            resource_type="ai_requests",
            quantity=12000  # Over the Pro plan limit
        )
        self.assertEqual(usage_result["status"], "success")

        # Simulate billing cycle end
        subscription = self.session.query(Subscription).get(subscription_id)
        invoice_data = {
            "id": "in_test",
            "subscription": subscription.stripe_subscription_id,
            "amount": 99.00,  # Base plan amount
            "status": "open"
        }
        
        invoice_result = self.billing_service._handle_invoice_paid(invoice_data)
        self.assertEqual(invoice_result["status"], "success")

        # Verify invoice includes overage charges
        invoice = self.session.query(Invoice).filter_by(
            subscription_id=subscription_id
        ).first()
        self.assertGreater(invoice.amount, 99.00)  # Should include overage charges

    def test_marketplace_integration(self):
        """Test marketplace functionality."""
        # Create marketplace item
        item_data = {
            "seller_id": 1,
            "name": "Custom Dashboard",
            "description": "Analytics dashboard template",
            "type": "dashboard",
            "price": 299.00
        }
        
        # Create purchase
        purchase_result = self.billing_service.process_marketplace_purchase(
            buyer_id=2,
            item_id=1,
            payment_method_id="pm_test_card"
        )
        self.assertEqual(purchase_result["status"], "success")

        # Verify commission calculation
        commission = purchase_result["commission"]
        self.assertEqual(commission, 44.85)  # 15% of $299.00

    def test_error_scenarios(self):
        """Test error handling in integrated scenarios."""
        # Test invalid plan upgrade
        with self.assertRaises(ValueError):
            self.billing_service.create_subscription(
                user_id=1,
                plan_id=999,  # Non-existent plan
                payment_method_id="pm_test_card"
            )

        # Test duplicate subscription
        subscription_result = self.billing_service.create_subscription(
            user_id=1,
            plan_id=2,
            payment_method_id="pm_test_card"
        )
        
        with self.assertRaises(ValueError):
            self.billing_service.create_subscription(
                user_id=1,
                plan_id=2,
                payment_method_id="pm_test_card"
            )

        # Test invalid usage tracking
        with self.assertRaises(ValueError):
            self.billing_service.track_usage(
                user_id=1,
                resource_type="invalid_resource",
                quantity=100
            )

if __name__ == "__main__":
    unittest.main() 