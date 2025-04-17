"""
Enterprise-grade performance and reliability tests for OmniData.AI billing system.
"""

import unittest
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from omnidata.billing.service import BillingService
from omnidata.billing.models import Plan, Subscription, Invoice
from omnidata.database import get_test_db

class TestEnterpriseBilling(unittest.TestCase):
    """Enterprise-grade billing system tests."""

    @classmethod
    def setUpClass(cls):
        """Initialize test environment with enterprise configuration."""
        cls.db = get_test_db()
        cls.billing_service = BillingService(cls.db)
        cls._create_enterprise_data()
        
        # Set up multi-lingual test data
        cls.test_currencies = ['USD', 'EUR', 'JPY', 'GBP']
        cls.test_languages = ['en', 'es', 'ja', 'de', 'fr']
        cls.test_regions = ['NA', 'EU', 'APAC', 'LATAM']

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    @classmethod
    def _create_enterprise_data(cls):
        """Create test data for enterprise scenarios."""
        # Create enterprise plans
        cls.enterprise_plan = Plan(
            name="Global Enterprise",
            tier="enterprise",
            price=Decimal('9999.99'),
            features={
                'max_users': 'unlimited',
                'storage_gb': 'unlimited',
                'support_level': '24/7',
                'regions': ['NA', 'EU', 'APAC', 'LATAM']
            }
        )
        cls.db.add(cls.enterprise_plan)
        cls.db.commit()

    def test_high_volume_transaction_processing(self):
        """Test processing of high-volume transactions with memory monitoring."""
        initial_memory = self._get_memory_usage()
        start_time = time.time()
        
        # Process 10,000 concurrent transactions
        transactions = []
        for i in range(10000):
            transaction = {
                'amount': Decimal('99.99'),
                'currency': self.test_currencies[i % len(self.test_currencies)],
                'region': self.test_regions[i % len(self.test_regions)],
                'language': self.test_languages[i % len(self.test_languages)]
            }
            transactions.append(transaction)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(
                lambda t: self.billing_service.process_international_payment(
                    user_id=1,
                    amount=t['amount'],
                    currency=t['currency']
                ),
                transactions
            ))
        
        execution_time = time.time() - start_time
        memory_increase = self._get_memory_usage() - initial_memory
        
        self.assertLess(execution_time, 30.0)  # Should complete within 30 seconds
        self.assertLess(memory_increase, 500)  # Memory increase should be less than 500MB
        self.assertEqual(len(results), 10000)

    @mock.patch('stripe.PaymentIntent')
    def test_global_payment_processing(self, mock_stripe):
        """Test multi-currency, global payment processing."""
        initial_memory = self._get_memory_usage()
        
        # Test payments in different currencies and regions
        test_cases = [
            {'amount': '99.99', 'currency': 'USD', 'region': 'NA', 'language': 'en'},
            {'amount': '89.99', 'currency': 'EUR', 'region': 'EU', 'language': 'de'},
            {'amount': '10000', 'currency': 'JPY', 'region': 'APAC', 'language': 'ja'},
            {'amount': '79.99', 'currency': 'GBP', 'region': 'EU', 'language': 'en'},
        ]
        
        for case in test_cases:
            result = self.billing_service.process_international_payment(
                user_id=1,
                amount=Decimal(case['amount']),
                currency=case['currency'],
                region=case['region'],
                language=case['language']
            )
            
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['currency'], case['currency'])
            
        memory_increase = self._get_memory_usage() - initial_memory
        self.assertLess(memory_increase, 50)  # Memory increase should be less than 50MB

    def test_enterprise_reporting(self):
        """Test generation of enterprise-level financial reports."""
        initial_memory = self._get_memory_usage()
        start_time = time.time()
        
        # Generate complex financial reports
        report = self.billing_service.generate_enterprise_report(
            report_type='financial',
            parameters={
                'regions': self.test_regions,
                'currencies': self.test_currencies,
                'languages': self.test_languages,
                'include_forecasting': True,
                'include_tax_calculations': True
            },
            start_date=datetime.now() - timedelta(days=365),
            end_date=datetime.now()
        )
        
        execution_time = time.time() - start_time
        memory_increase = self._get_memory_usage() - initial_memory
        
        self.assertLess(execution_time, 10.0)  # Should complete within 10 seconds
        self.assertLess(memory_increase, 200)  # Memory increase should be less than 200MB
        self.assertIn('revenue_by_region', report)
        self.assertIn('tax_summary', report)

    def test_disaster_recovery(self):
        """Test system resilience and disaster recovery capabilities."""
        # Simulate database failure
        with mock.patch.object(self.db, 'commit', side_effect=Exception('Database connection lost')):
            result = self.billing_service.process_with_failover(
                operation='create_subscription',
                user_id=1,
                plan_id=self.enterprise_plan.id
            )
            
            self.assertEqual(result['status'], 'success')
            self.assertTrue(result['used_failover'])
            
        # Verify data consistency after recovery
        consistency_check = self.billing_service.verify_data_consistency(
            start_date=datetime.now() - timedelta(hours=1)
        )
        self.assertTrue(consistency_check['is_consistent'])

    def test_compliance_and_audit(self):
        """Test compliance requirements and audit trail generation."""
        # Create a series of sensitive operations
        operations = [
            {
                'type': 'subscription_update',
                'data': {'plan_id': self.enterprise_plan.id}
            },
            {
                'type': 'payment_process',
                'data': {'amount': '9999.99', 'currency': 'USD'}
            },
            {
                'type': 'user_data_access',
                'data': {'user_id': 1, 'data_type': 'financial'}
            }
        ]
        
        audit_records = []
        for op in operations:
            result = self.billing_service.process_with_audit(
                operation=op['type'],
                parameters=op['data'],
                audit_level='detailed'
            )
            audit_records.append(result['audit_record'])
        
        # Verify audit trail
        verification = self.billing_service.verify_audit_trail(audit_records)
        self.assertTrue(verification['is_valid'])
        self.assertFalse(verification['tampering_detected'])
        
        # Test compliance data
        compliance_data = self.billing_service._get_compliance_data(user_id=1)
        self.assertIn('gdpr_status', compliance_data)
        self.assertIn('data_retention_policy', compliance_data)
        self.assertIn('audit_history', compliance_data)

if __name__ == '__main__':
    unittest.main() 