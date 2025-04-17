"""
Performance tests for billing system.
"""

import unittest
import time
import psutil
import mock
from datetime import datetime, timedelta
import concurrent.futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from omnidata.database import Base
from omnidata.billing.models import Plan, Subscription, Usage
from omnidata.billing.service import BillingService
from omnidata.billing.utils import calculate_usage_cost, check_resource_limits

class TestBillingPerformance(unittest.TestCase):
    """Performance tests for billing system."""

    @classmethod
    def setUpClass(cls):
        """Set up test database and service."""
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        Session = sessionmaker(bind=cls.engine)
        cls.session = Session()
        cls.billing_service = BillingService(cls.session)
        cls._create_test_data()

    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.session.close()
        Base.metadata.drop_all(cls.engine)

    @classmethod
    def _create_test_data(cls):
        """Create test data for performance testing."""
        # Create plans
        plans = [
            Plan(name=f"Plan {i}", tier="pro", price=99.00)
            for i in range(100)
        ]
        cls.session.bulk_save_objects(plans)
        
        # Create subscriptions
        subscriptions = [
            Subscription(
                user_id=i,
                plan_id=1,
                status="active",
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=30)
            )
            for i in range(1000)
        ]
        cls.session.bulk_save_objects(subscriptions)
        
        # Create usage records
        usage_records = [
            Usage(
                user_id=i % 1000,
                resource_type="ai_requests",
                quantity=100,
                timestamp=datetime.now() - timedelta(days=i % 30)
            )
            for i in range(10000)
        ]
        cls.session.bulk_save_objects(usage_records)
        cls.session.commit()

    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def test_usage_calculation_performance(self):
        """Test performance of usage calculations."""
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        # Calculate usage for 1000 users
        for user_id in range(1000):
            metrics = self.billing_service.get_usage_metrics(
                user_id=user_id,
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now()
            )
            self.assertEqual(metrics["status"], "success")
        
        duration = time.time() - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertLess(duration, 5.0)  # Should complete within 5 seconds
        self.assertLess(memory_increase, 100)  # Memory increase should be less than 100MB
        print(f"Usage calculation time: {duration:.2f}s, Memory increase: {memory_increase:.2f}MB")

    def test_concurrent_usage_tracking(self):
        """Test concurrent usage tracking performance."""
        def track_usage(user_id):
            return self.billing_service.track_usage(
                user_id=user_id,
                resource_type="ai_requests",
                quantity=100
            )

        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(track_usage, user_id)
                for user_id in range(100)
            ]
            results = [future.result() for future in futures]
        
        duration = time.time() - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertLess(duration, 2.0)  # Should complete within 2 seconds
        self.assertLess(memory_increase, 50)  # Memory increase should be less than 50MB
        print(f"Concurrent tracking time: {duration:.2f}s, Memory increase: {memory_increase:.2f}MB")

    @mock.patch('stripe.Subscription')
    def test_stripe_integration_performance(self, mock_stripe):
        """Test performance with mocked Stripe integration."""
        mock_stripe.create.return_value = {"id": "sub_test", "status": "active"}
        mock_stripe.modify.return_value = {"id": "sub_test", "status": "active"}
        
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        # Test 100 subscription operations
        for i in range(100):
            result = self.billing_service.create_subscription(
                user_id=i,
                plan_id=1,
                payment_method_id="pm_test"
            )
            self.assertEqual(result["status"], "success")
        
        duration = time.time() - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertLess(duration, 3.0)  # Should complete within 3 seconds
        self.assertLess(memory_increase, 30)  # Memory increase should be less than 30MB
        print(f"Stripe integration time: {duration:.2f}s, Memory increase: {memory_increase:.2f}MB")

    def test_bulk_subscription_processing(self):
        """Test performance of bulk subscription processing."""
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        # Process 1000 subscriptions
        subscriptions = self.session.query(Subscription).limit(1000).all()
        for subscription in subscriptions:
            self.billing_service._handle_subscription_updated({
                "id": subscription.id,
                "status": "active",
                "current_period_end": datetime.now() + timedelta(days=30)
            })
        
        duration = time.time() - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertLess(duration, 3.0)  # Should complete within 3 seconds
        self.assertLess(memory_increase, 75)  # Memory increase should be less than 75MB
        print(f"Bulk processing time: {duration:.2f}s, Memory increase: {memory_increase:.2f}MB")

    @mock.patch('redis.Redis')
    def test_cache_performance(self, mock_redis):
        """Test performance with Redis caching."""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        # Test 1000 cache operations
        for i in range(1000):
            key = f"test_key_{i}"
            value = f"test_value_{i}"
            mock_redis.set(key, value)
            result = mock_redis.get(key)
        
        duration = time.time() - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertLess(duration, 1.0)  # Should complete within 1 second
        self.assertLess(memory_increase, 20)  # Memory increase should be less than 20MB
        print(f"Cache operation time: {duration:.2f}s, Memory increase: {memory_increase:.2f}MB")

    def test_load_testing(self):
        """Simulate load testing with multiple concurrent operations."""
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        def mixed_workload(i):
            # Simulate mixed operations
            self.billing_service.track_usage(i % 100, "ai_requests", 100)
            self.billing_service.get_usage_metrics(
                i % 100,
                datetime.now() - timedelta(days=30),
                datetime.now()
            )
            check_resource_limits(
                {"ai_requests": 100},
                {"ai_requests": 1000}
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(mixed_workload, range(500)))
        
        duration = time.time() - start_time
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        self.assertLess(duration, 10.0)  # Should complete within 10 seconds
        self.assertLess(memory_increase, 150)  # Memory increase should be less than 150MB
        print(f"Load test time: {duration:.2f}s, Memory increase: {memory_increase:.2f}MB")

if __name__ == '__main__':
    unittest.main()

 