"""
Secure key management service for OmniData.AI
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from redis import Redis
from sqlalchemy.orm import Session
from omnidata.database import get_db
from omnidata.utils.logging import get_logger

logger = get_logger(__name__)

class KeyManager:
    def __init__(self, redis_client: Redis = None):
        self.redis = redis_client or Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379))
        )
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.fernet = Fernet(self.encryption_key.encode())
        
    def get_api_key(self, service: str) -> str:
        """Get API key with usage tracking."""
        key = self._get_from_cache(f"api_key:{service}")
        if not key:
            key = os.getenv(f"{service.upper()}_API_KEY")
            self._cache_key(f"api_key:{service}", key)
        
        self._track_key_usage(service)
        return key
    
    def rotate_key(self, service: str, new_key: str) -> bool:
        """Rotate API key with validation."""
        try:
            old_key = self.get_api_key(service)
            encrypted_old_key = self.fernet.encrypt(old_key.encode())
            
            # Store old key for potential rollback
            self.redis.setex(
                f"old_key:{service}",
                timedelta(days=7),
                encrypted_old_key
            )
            
            # Update with new key
            self._cache_key(f"api_key:{service}", new_key)
            self._log_key_rotation(service)
            
            return True
        except Exception as e:
            logger.error(f"Key rotation failed for {service}: {str(e)}")
            return False
    
    def validate_key_usage(self, service: str) -> Dict[str, Any]:
        """Validate key usage patterns."""
        usage_key = f"key_usage:{service}"
        current_usage = int(self.redis.get(usage_key) or 0)
        threshold = int(os.getenv('SECURITY_ALERT_THRESHOLD', 100))
        
        return {
            "service": service,
            "current_usage": current_usage,
            "threshold": threshold,
            "exceeded": current_usage > threshold
        }
    
    def _track_key_usage(self, service: str) -> None:
        """Track API key usage."""
        usage_key = f"key_usage:{service}"
        pipe = self.redis.pipeline()
        pipe.incr(usage_key)
        pipe.expire(usage_key, timedelta(days=1))
        pipe.execute()
        
        # Check for suspicious usage
        self._check_suspicious_activity(service)
    
    def _check_suspicious_activity(self, service: str) -> None:
        """Monitor for suspicious API key usage."""
        usage = self.validate_key_usage(service)
        if usage["exceeded"]:
            logger.warning(f"Suspicious activity detected for {service}")
            self._send_security_alert(service, usage)
    
    def _send_security_alert(self, service: str, usage: Dict[str, Any]) -> None:
        """Send security alerts for suspicious activity."""
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self._send_telegram_alert(
                f"🚨 Security Alert: High API usage detected for {service}\n"
                f"Current usage: {usage['current_usage']}\n"
                f"Threshold: {usage['threshold']}"
            )
    
    def _send_telegram_alert(self, message: str) -> None:
        """Send alert via Telegram."""
        import requests
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if bot_token and chat_id:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {str(e)}")
    
    def _cache_key(self, key: str, value: str) -> None:
        """Cache API key with encryption."""
        encrypted_value = self.fernet.encrypt(value.encode())
        self.redis.setex(
            key,
            timedelta(days=int(os.getenv('KEY_ROTATION_INTERVAL_DAYS', 30))),
            encrypted_value
        )
    
    def _get_from_cache(self, key: str) -> Optional[str]:
        """Get and decrypt cached API key."""
        encrypted_value = self.redis.get(key)
        if encrypted_value:
            try:
                return self.fernet.decrypt(encrypted_value).decode()
            except Exception:
                return None
        return None
    
    def _log_key_rotation(self, service: str) -> None:
        """Log key rotation events."""
        log_entry = {
            "service": service,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "key_rotation"
        }
        
        logger.info(f"Key rotation event: {json.dumps(log_entry)}")
        
        # Store in audit log
        self.redis.lpush(
            "key_rotation_audit_log",
            json.dumps(log_entry)
        )
        self.redis.ltrim(
            "key_rotation_audit_log",
            0,
            999  # Keep last 1000 rotation events
        ) 