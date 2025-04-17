"""
Unit tests for billing utility functions.
"""

import unittest
from datetime import datetime, timedelta
import os
from decimal import Decimal
from omnidata.billing.utils import (
    calculate_prorated_amount,
    calculate_usage_cost,
    get_plan_features,
    calculate_marketplace_commission,
    validate_addon_price,
    calculate_subscription_metrics,
    format_invoice_line_items,
    check_resource_limits
)

class TestBillingUtils(unittest.TestCase):
    """Test cases for billing utility functions."""

    def setUp(self):
        """Set up test environment variables."""
        os.environ["FREE_TIER_LIMITS_AI_REQUESTS"] = "100"
        os.environ["FREE_TIER_LIMITS_STORAGE_GB"] = "5"
        os.environ["FREE_TIER_LIMITS_DOMAINS"] = "1"
        os.environ["PRO_TIER_LIMITS_AI_REQUESTS"] = "10000"
        os.environ["PRO_TIER_LIMITS_STORAGE_GB"] = "50"
        os.environ["PRO_TIER_LIMITS_DOMAINS"] = "5"
        os.environ["MARKETPLACE_COMMISSION_RATE"] = "0.15"
        os.environ["ADDON_MODEL_PACK_MIN_PRICE"] = "499"
        os.environ["ADDON_DASHBOARD_PACK_MIN_PRICE"] = "299"
        os.environ["ADDON_FINETUNING_MIN_PRICE"] = "1500"
        os.environ["AI_REQUESTS_OVERAGE_RATE"] = "0.01"
        os.environ["STORAGE_GB_OVERAGE_RATE"] = "0.50"

    def test_calculate_prorated_amount(self):
        """Test proration calculations."""
        # Test monthly proration
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 15)  # 15 days
        base_amount = 100.00

        prorated = calculate_prorated_amount(
            base_amount=base_amount,
            start_date=start_date,
            end_date=end_date,
            billing_interval="month"
        )
        self.assertEqual(prorated, 50.00)  # Half month = half price

        # Test yearly proration
        end_date = datetime(2024, 7, 1)  # 6 months
        prorated = calculate_prorated_amount(
            base_amount=base_amount,
            start_date=start_date,
            end_date=end_date,
            billing_interval="year"
        )
        self.assertEqual(prorated, 49.59)  # ~Half year (181/365 days)

    def test_calculate_usage_cost(self):
        """Test usage-based cost calculations."""
        # Test within limits
        cost, within_limits = calculate_usage_cost(
            usage_quantity=50,
            plan_limits={"ai_requests_included": 100},
            resource_type="ai_requests"
        )
        self.assertEqual(cost, 0.00)
        self.assertTrue(within_limits)

        # Test over limits
        cost, within_limits = calculate_usage_cost(
            usage_quantity=150,
            plan_limits={"ai_requests_included": 100},
            resource_type="ai_requests"
        )
        self.assertEqual(cost, 0.50)  # 50 excess requests * $0.01
        self.assertFalse(within_limits)

    def test_get_plan_features(self):
        """Test plan feature retrieval."""
        # Test free tier
        free_features = get_plan_features("free")
        self.assertEqual(free_features["ai_requests"], 100)
        self.assertEqual(free_features["storage_gb"], 5)
        self.assertEqual(free_features["domains"], 1)
        self.assertTrue(free_features["features"]["basic_analytics"])
        self.assertFalse(free_features["features"]["api_access"])

        # Test pro tier
        pro_features = get_plan_features("pro")
        self.assertEqual(pro_features["ai_requests"], 10000)
        self.assertEqual(pro_features["storage_gb"], 50)
        self.assertEqual(pro_features["domains"], 5)
        self.assertTrue(pro_features["features"]["api_access"])
        self.assertTrue(pro_features["features"]["custom_models"])

        # Test enterprise tier
        enterprise_features = get_plan_features("enterprise")
        self.assertEqual(enterprise_features["ai_requests"], float('inf'))
        self.assertTrue(enterprise_features["features"]["dedicated_support"])

    def test_calculate_marketplace_commission(self):
        """Test marketplace commission calculations."""
        # Test default commission rate
        commission = calculate_marketplace_commission(100.00)
        self.assertEqual(commission, 15.00)  # 15% of $100

        # Test custom commission rate
        commission = calculate_marketplace_commission(100.00, commission_rate=0.20)
        self.assertEqual(commission, 20.00)  # 20% of $100

        # Test decimal precision
        commission = calculate_marketplace_commission(99.99)
        self.assertEqual(commission, 15.00)  # 15% of $99.99, rounded

    def test_validate_addon_price(self):
        """Test add-on price validation."""
        # Test model pack pricing
        self.assertTrue(validate_addon_price("model_pack", 500.00))
        self.assertFalse(validate_addon_price("model_pack", 498.99))

        # Test dashboard pack pricing
        self.assertTrue(validate_addon_price("dashboard_pack", 300.00))
        self.assertFalse(validate_addon_price("dashboard_pack", 298.99))

        # Test fine-tuning pricing
        self.assertTrue(validate_addon_price("finetuning", 1500.00))
        self.assertFalse(validate_addon_price("finetuning", 1499.99))

        # Test unknown add-on type
        self.assertTrue(validate_addon_price("custom_type", 10.00))

    def test_calculate_subscription_metrics(self):
        """Test subscription metrics calculations."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        subscriptions = [
            {
                "status": "active",
                "plan_amount": 99.00,
                "current_period_end": datetime(2024, 1, 15)
            },
            {
                "status": "active",
                "plan_amount": 99.00,
                "current_period_end": datetime(2024, 1, 20)
            },
            {
                "status": "canceled",
                "plan_amount": 99.00,
                "canceled_at": datetime(2024, 1, 10)
            }
        ]

        metrics = calculate_subscription_metrics(subscriptions, start_date, end_date)
        self.assertEqual(metrics["mrr"], 198.00)  # 2 active subscriptions
        self.assertEqual(metrics["active_subscriptions"], 2)
        self.assertEqual(metrics["churned_subscriptions"], 1)
        self.assertEqual(metrics["churn_rate"], 50.00)  # 1/2 * 100

    def test_format_invoice_line_items(self):
        """Test invoice line item formatting."""
        items = [
            {
                "description": "Monthly Subscription",
                "unit_price": 99.99,
                "amount": 99.99
            },
            {
                "description": "Usage Overage",
                "quantity": 50,
                "unit_price": 0.01,
                "amount": 0.50
            }
        ]

        formatted = format_invoice_line_items(items)
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]["amount"], 99.99)
        self.assertEqual(formatted[1]["quantity"], 50)
        self.assertEqual(formatted[1]["amount"], 0.50)
        self.assertEqual(formatted[1]["currency"], "USD")

    def test_check_resource_limits(self):
        """Test resource limit checking."""
        current_usage = {
            "ai_requests": 75,
            "storage_gb": 4,
            "domains": 1
        }

        plan_limits = {
            "ai_requests": 100,
            "storage_gb": 5,
            "domains": 1
        }

        status = check_resource_limits(current_usage, plan_limits)
        
        # Test AI requests
        self.assertEqual(status["ai_requests"]["current"], 75)
        self.assertEqual(status["ai_requests"]["limit"], 100)
        self.assertEqual(status["ai_requests"]["percentage"], 75.0)
        self.assertTrue(status["ai_requests"]["within_limit"])

        # Test storage
        self.assertEqual(status["storage_gb"]["current"], 4)
        self.assertEqual(status["storage_gb"]["percentage"], 80.0)
        self.assertTrue(status["storage_gb"]["within_limit"])

        # Test domains
        self.assertEqual(status["domains"]["current"], 1)
        self.assertEqual(status["domains"]["percentage"], 100.0)
        self.assertTrue(status["domains"]["within_limit"])

    def test_calculate_prorated_amount_errors(self):
        """Test error handling in proration calculations."""
        # Test end date before start date
        with self.assertRaises(ValueError) as context:
            calculate_prorated_amount(
                base_amount=100.00,
                start_date=datetime(2024, 1, 15),
                end_date=datetime(2024, 1, 1),
                billing_interval="month"
            )
        self.assertIn("End date must be after start date", str(context.exception))

        # Test invalid billing interval
        with self.assertRaises(ValueError) as context:
            calculate_prorated_amount(
                base_amount=100.00,
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 15),
                billing_interval="invalid"
            )
        self.assertIn("Invalid billing interval", str(context.exception))

        # Test negative base amount
        with self.assertRaises(ValueError) as context:
            calculate_prorated_amount(
                base_amount=-100.00,
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 15),
                billing_interval="month"
            )
        self.assertIn("Base amount must be positive", str(context.exception))

    def test_calculate_usage_cost_errors(self):
        """Test error handling in usage cost calculations."""
        # Test negative usage quantity
        with self.assertRaises(ValueError) as context:
            calculate_usage_cost(
                usage_quantity=-50,
                plan_limits={"ai_requests_included": 100},
                resource_type="ai_requests"
            )
        self.assertIn("Usage quantity must be non-negative", str(context.exception))

        # Test missing plan limits
        with self.assertRaises(KeyError) as context:
            calculate_usage_cost(
                usage_quantity=50,
                plan_limits={},
                resource_type="ai_requests"
            )
        self.assertIn("Plan limits not found", str(context.exception))

        # Test unknown resource type
        with self.assertRaises(ValueError) as context:
            calculate_usage_cost(
                usage_quantity=50,
                plan_limits={"unknown_included": 100},
                resource_type="unknown"
            )
        self.assertIn("Unknown resource type", str(context.exception))

    def test_get_plan_features_errors(self):
        """Test error handling in plan feature retrieval."""
        # Test invalid plan tier
        with self.assertRaises(ValueError) as context:
            get_plan_features("invalid_tier")
        self.assertIn("Invalid plan tier", str(context.exception))

        # Test missing environment variables
        original_value = os.environ.get("FREE_TIER_LIMITS_AI_REQUESTS")
        del os.environ["FREE_TIER_LIMITS_AI_REQUESTS"]
        
        features = get_plan_features("free")
        self.assertEqual(features["ai_requests"], 100)  # Should use default value
        
        if original_value:
            os.environ["FREE_TIER_LIMITS_AI_REQUESTS"] = original_value

    def test_calculate_marketplace_commission_errors(self):
        """Test error handling in marketplace commission calculations."""
        # Test negative sale amount
        with self.assertRaises(ValueError) as context:
            calculate_marketplace_commission(-100.00)
        self.assertIn("Sale amount must be positive", str(context.exception))

        # Test invalid commission rate
        with self.assertRaises(ValueError) as context:
            calculate_marketplace_commission(100.00, commission_rate=-0.1)
        self.assertIn("Commission rate must be between 0 and 1", str(context.exception))

        with self.assertRaises(ValueError) as context:
            calculate_marketplace_commission(100.00, commission_rate=1.5)
        self.assertIn("Commission rate must be between 0 and 1", str(context.exception))

    def test_calculate_subscription_metrics_errors(self):
        """Test error handling in subscription metrics calculations."""
        # Test invalid date range
        with self.assertRaises(ValueError) as context:
            calculate_subscription_metrics(
                [],
                start_date=datetime(2024, 1, 31),
                end_date=datetime(2024, 1, 1)
            )
        self.assertIn("End date must be after start date", str(context.exception))

        # Test invalid subscription status
        subscriptions = [{
            "status": "invalid",
            "plan_amount": 99.00,
            "current_period_end": datetime(2024, 1, 15)
        }]
        
        with self.assertRaises(ValueError) as context:
            calculate_subscription_metrics(
                subscriptions,
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31)
            )
        self.assertIn("Invalid subscription status", str(context.exception))

    def test_format_invoice_line_items_errors(self):
        """Test error handling in invoice line item formatting."""
        # Test missing required fields
        items = [{
            "description": "Monthly Subscription"
            # Missing unit_price and amount
        }]
        
        with self.assertRaises(KeyError) as context:
            format_invoice_line_items(items)
        self.assertIn("Missing required fields", str(context.exception))

        # Test negative amounts
        items = [{
            "description": "Monthly Subscription",
            "unit_price": -99.99,
            "amount": -99.99
        }]
        
        with self.assertRaises(ValueError) as context:
            format_invoice_line_items(items)
        self.assertIn("Amount must be non-negative", str(context.exception))

    def test_check_resource_limits_errors(self):
        """Test error handling in resource limit checking."""
        # Test negative usage values
        current_usage = {
            "ai_requests": -75,
            "storage_gb": 4
        }
        
        with self.assertRaises(ValueError) as context:
            check_resource_limits(current_usage, {"ai_requests": 100})
        self.assertIn("Usage values must be non-negative", str(context.exception))

        # Test negative limit values
        plan_limits = {
            "ai_requests": -100
        }
        
        with self.assertRaises(ValueError) as context:
            check_resource_limits({"ai_requests": 75}, plan_limits)
        self.assertIn("Limit values must be non-negative", str(context.exception))

if __name__ == "__main__":
    unittest.main() 