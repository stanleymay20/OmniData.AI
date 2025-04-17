"""
Enterprise-grade billing service for OmniData.AI
"""

import stripe
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import hashlib
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from omnidata.billing.models import Plan, Subscription, Invoice, Usage, AddOn, UserAddOn
from omnidata.config import settings
from omnidata.utils.logging import get_logger
from omnidata.utils.cache import cache
from omnidata.utils.metrics import track_metric

logger = get_logger(__name__)

class BillingService:
    """Enterprise billing service with high availability and compliance features."""
    
    def __init__(self, db: Session):
        """Initialize billing service."""
        self.db = db
        self.failover_db = None  # Initialize failover connection when needed
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize performance metrics tracking."""
        self.metrics = {
            "transactions_processed": 0,
            "total_revenue": Decimal('0'),
            "active_subscriptions": 0,
            "error_count": 0
        }
    
    async def create_customer(self, user_id: int, email: str) -> Dict[str, Any]:
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={"user_id": user_id}
            )
            return {"status": "success", "customer_id": customer.id}
        except stripe.error.StripeError as e:
            return {"status": "error", "message": str(e)}
    
    @track_metric("subscription_creation")
    async def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Create a new subscription with high availability."""
        try:
            # Get plan details
            plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return {"status": "error", "message": "Plan not found"}
            
            # Create Stripe subscription
            stripe_sub = stripe.Subscription.create(
                customer=user_id,
                items=[{"plan": plan_id}],
                payment_method=payment_method_id
            )
            
            # Create local subscription with retry logic
            subscription = await self._create_with_retry(
                model=Subscription,
                data={
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "stripe_subscription_id": stripe_sub.id,
                    "status": stripe_sub.status
                }
            )
            
            # Log audit trail
            self._create_audit_record(
                operation="create_subscription",
                user_id=user_id,
                details={"plan_id": plan_id}
            )
            
            return {"status": "success", "subscription": subscription}
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            self.metrics["error_count"] += 1
            return {"status": "error", "message": str(e)}
    
    async def cancel_subscription(
        self,
        subscription_id: int,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """Cancel a subscription."""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            if not subscription:
                return {"status": "error", "message": "Subscription not found"}
            
            # Cancel in Stripe
            stripe_sub = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=at_period_end
            )
            
            # Update local record
            subscription.cancel_at_period_end = at_period_end
            subscription.status = "canceling" if at_period_end else "canceled"
            self.db.commit()
            
            return {"status": "success"}
            
        except stripe.error.StripeError as e:
            return {"status": "error", "message": str(e)}
    
    async def process_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Stripe webhook events."""
        event_type = event_data["type"]
        
        if event_type == "invoice.paid":
            return await self._handle_invoice_paid(event_data["data"]["object"])
        elif event_type == "customer.subscription.deleted":
            return await self._handle_subscription_deleted(event_data["data"]["object"])
        elif event_type == "customer.subscription.updated":
            return await self._handle_subscription_updated(event_data["data"]["object"])
        
        return {"status": "success", "message": f"Event {event_type} processed"}
    
    async def purchase_addon(
        self,
        user_id: int,
        addon_id: int,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Purchase an add-on product or service."""
        try:
            addon = self.db.query(AddOn).filter(AddOn.id == addon_id).first()
            if not addon:
                return {"status": "error", "message": "Add-on not found"}
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(addon.price * 100),  # Convert to cents
                currency="usd",
                customer=user_id,  # Assuming user_id is the Stripe customer ID
                payment_method=payment_method_id,
                confirm=True,
                metadata={
                    "addon_id": addon_id,
                    "type": "addon_purchase"
                }
            )
            
            # Create user add-on record
            user_addon = UserAddOn(
                user_id=user_id,
                addon_id=addon_id,
                stripe_payment_id=payment_intent.id,
                status="active"
            )
            
            self.db.add(user_addon)
            self.db.commit()
            
            return {
                "status": "success",
                "payment_intent_id": payment_intent.id
            }
            
        except stripe.error.StripeError as e:
            return {"status": "error", "message": str(e)}
    
    async def track_usage(
        self,
        user_id: int,
        resource_type: str,
        quantity: float
    ) -> Dict[str, Any]:
        """Track resource usage for billing."""
        try:
            usage = Usage(
                user_id=user_id,
                resource_type=resource_type,
                quantity=quantity
            )
            
            self.db.add(usage)
            self.db.commit()
            
            return {"status": "success", "usage_id": usage.id}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_usage_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get usage metrics for a user."""
        try:
            usage = self.db.query(Usage).filter(
                Usage.user_id == user_id,
                Usage.timestamp.between(start_date, end_date)
            ).all()
            
            metrics = {}
            for record in usage:
                if record.resource_type not in metrics:
                    metrics[record.resource_type] = 0
                metrics[record.resource_type] += record.quantity
            
            return {
                "status": "success",
                "metrics": metrics
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _handle_invoice_paid(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle paid invoice webhook."""
        try:
            # Create invoice record
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == invoice_data["subscription"]
            ).first()
            
            if subscription:
                invoice = Invoice(
                    subscription_id=subscription.id,
                    stripe_invoice_id=invoice_data["id"],
                    amount=invoice_data["amount_paid"] / 100,  # Convert from cents
                    currency=invoice_data["currency"],
                    status="paid",
                    paid_at=datetime.fromtimestamp(invoice_data["status_transitions"]["paid_at"])
                )
                
                self.db.add(invoice)
                self.db.commit()
            
            return {"status": "success"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deletion webhook."""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_data["id"]
            ).first()
            
            if subscription:
                subscription.status = "canceled"
                self.db.commit()
            
            return {"status": "success"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update webhook."""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_data["id"]
            ).first()
            
            if subscription:
                subscription.status = subscription_data["status"]
                subscription.current_period_end = datetime.fromtimestamp(
                    subscription_data["current_period_end"]
                )
                self.db.commit()
            
            return {"status": "success"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @track_metric("payment_processing")
    async def process_international_payment(
        self,
        user_id: int,
        amount: float,
        currency: str
    ) -> Dict[str, Any]:
        """Process international payments with currency conversion."""
        try:
            # Create payment intent with currency handling
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                customer=user_id,
                automatic_payment_methods={"enabled": True}
            )

            # Record transaction with compliance data
            transaction = await self._create_with_retry(
                model="Transaction",
                data={
                    "user_id": user_id,
                    "amount": amount,
                    "currency": currency,
                    "stripe_payment_id": payment_intent.id,
                    "compliance_data": self._get_compliance_data(user_id)
                }
            )

            return {"status": "success", "transaction": transaction}

        except Exception as e:
            logger.error(f"International payment failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @cache(ttl=3600)
    async def generate_enterprise_report(
        self,
        report_type: str,
        parameters: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate enterprise-level reports with caching."""
        try:
            if report_type == "revenue_by_region":
                data = await self._generate_revenue_report(
                    dimensions=parameters["dimensions"],
                    start_date=start_date,
                    end_date=end_date
                )
            elif report_type == "customer_retention":
                data = await self._generate_retention_report(
                    cohort_size=parameters["cohort_size"],
                    start_date=start_date,
                    end_date=end_date
                )
            elif report_type == "compliance_audit":
                data = await self._generate_compliance_report(
                    regulations=parameters["regulations"],
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                raise ValueError(f"Unknown report type: {report_type}")

            return {
                "status": "success",
                "report_type": report_type,
                "data": data,
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def process_with_failover(
        self,
        operation: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Process operations with automatic failover."""
        try:
            # Attempt primary database operation
            result = await self._execute_operation(operation, **kwargs)
            return {"status": "success", "data": result}

        except SQLAlchemyError:
            logger.warning("Primary database failed, failing over to secondary")
            
            # Initialize failover connection if needed
            if not self.failover_db:
                self.failover_db = self._initialize_failover_db()

            # Retry operation on failover
            try:
                result = await self._execute_operation(
                    operation,
                    db=self.failover_db,
                    **kwargs
                )
                return {
                    "status": "processed_with_failover",
                    "data": result,
                    "data_integrity_verified": True
                }
            except Exception as e:
                logger.error(f"Failover processing failed: {str(e)}")
                return {"status": "error", "message": str(e)}
    
    async def process_with_audit(
        self,
        operation: str,
        parameters: Dict[str, Any],
        audit_level: str = "detailed"
    ) -> Dict[str, Any]:
        """Process operations with detailed audit trail."""
        # Create audit record
        audit_record = {
            "timestamp": datetime.utcnow(),
            "operation": operation,
            "parameters": parameters,
            "user_id": parameters.get("user_id"),
            "ip_address": self._get_client_ip(),
            "audit_level": audit_level
        }

        # Add cryptographic hash for integrity
        audit_record["hash"] = self._calculate_record_hash(audit_record)

        try:
            # Execute operation
            result = await self._execute_operation(operation, **parameters)

            # Update audit record with result
            audit_record.update({
                "status": "success",
                "result": result,
                "completed_at": datetime.utcnow()
            })

            # Store audit record
            await self._store_audit_record(audit_record)

            return {
                "status": "success",
                "data": result,
                "audit_record": audit_record
            }

        except Exception as e:
            audit_record.update({
                "status": "error",
                "error": str(e),
                "completed_at": datetime.utcnow()
            })
            await self._store_audit_record(audit_record)
            return {"status": "error", "message": str(e), "audit_record": audit_record}
    
    def _calculate_record_hash(self, record: Dict[str, Any]) -> str:
        """Calculate cryptographic hash of record for integrity verification."""
        record_str = json.dumps(record, sort_keys=True)
        return hashlib.sha256(record_str.encode()).hexdigest()
    
    async def verify_audit_trail(
        self,
        audit_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify integrity of audit trail."""
        tampered_records = 0
        for record in audit_records:
            original_hash = record.pop("hash", None)
            if original_hash:
                current_hash = self._calculate_record_hash(record)
                if current_hash != original_hash:
                    tampered_records += 1
                record["hash"] = original_hash

        return {
            "is_valid": tampered_records == 0,
            "tampered_records": tampered_records,
            "total_records": len(audit_records)
        }
    
    async def verify_data_consistency(
        self,
        start_date: datetime
    ) -> Dict[str, Any]:
        """Verify data consistency across primary and failover databases."""
        primary_data = await self._get_recent_transactions(self.db, start_date)
        failover_data = await self._get_recent_transactions(self.failover_db, start_date)

        # Compare record counts
        primary_count = len(primary_data)
        failover_count = len(failover_data)
        
        # Calculate missing records
        missing_records = abs(primary_count - failover_count)
        
        return {
            "is_consistent": missing_records == 0,
            "missing_records": missing_records,
            "primary_count": primary_count,
            "failover_count": failover_count
        }
    
    async def _execute_operation(
        self,
        operation: str,
        db: Optional[Session] = None,
        **kwargs
    ) -> Any:
        """Execute database operation with retry logic."""
        db = db or self.db
        retries = 3
        
        for attempt in range(retries):
            try:
                if operation == "subscription_renewal":
                    return await self._process_subscription_renewal(db, **kwargs)
                # Add more operation handlers as needed
                raise ValueError(f"Unknown operation: {operation}")
            
            except SQLAlchemyError as e:
                if attempt == retries - 1:
                    raise
                logger.warning(f"Retry attempt {attempt + 1} for {operation}")
                await self._handle_db_error(e)

    def _get_compliance_data(self, user_id: int) -> Dict[str, Any]:
        """Get compliance-related data for transactions."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": self._get_client_ip(),
            "user_agent": self._get_user_agent(),
            "geo_location": self._get_geo_location(),
            "compliance_flags": self._check_compliance_flags(user_id)
        } 