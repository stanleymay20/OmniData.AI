import logging
from datetime import datetime
from typing import Dict, Optional

class KeyManager:
    def __init__(self):
        self.api_keys = {}
        self.usage_limits = {
            'free': 1000,  # Free tier limit
            'basic': 10000,  # Basic tier limit
            'pro': 100000,  # Pro tier limit
            'enterprise': float('inf')  # Enterprise tier limit
        }
        self.alert_thresholds = {
            'usage_warning': 0.8,  # 80% of limit
            'usage_critical': 0.9,  # 90% of limit
            'rate_limit': 100,  # Requests per minute
            'concurrent_limit': 50  # Concurrent requests
        }
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add file handler for detailed logging
        file_handler = logging.FileHandler('key_manager.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def validate_key(self, api_key: str) -> bool:
        """Validate API key with enhanced security checks."""
        try:
            if not api_key or len(api_key) != 32:
                self.logger.warning(f"Invalid API key format: {api_key}")
                return False
                
            if api_key not in self.api_keys:
                self.logger.warning(f"Unknown API key: {api_key}")
                return False
                
            key_info = self.api_keys[api_key]
            if key_info['expires_at'] < datetime.now():
                self.logger.warning(f"Expired API key: {api_key}")
                return False
                
            # Check rate limiting
            current_time = datetime.now()
            if 'last_request' in key_info:
                time_diff = (current_time - key_info['last_request']).total_seconds()
                if time_diff < 60 and key_info['requests_in_window'] >= self.alert_thresholds['rate_limit']:
                    self.logger.warning(f"Rate limit exceeded for key: {api_key}")
                    return False
                    
            # Update request tracking
            key_info['last_request'] = current_time
            key_info['requests_in_window'] = key_info.get('requests_in_window', 0) + 1
            
            # Check usage limits
            tier_limit = self.usage_limits[key_info['tier']]
            current_usage = key_info.get('usage_count', 0)
            
            if current_usage >= tier_limit:
                self.logger.warning(f"Usage limit exceeded for key: {api_key}")
                return False
                
            # Check for suspicious patterns
            if self._detect_suspicious_pattern(api_key, key_info):
                self.logger.warning(f"Suspicious activity detected for key: {api_key}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating API key: {str(e)}")
            return False

    def _detect_suspicious_pattern(self, api_key: str, key_info: Dict) -> bool:
        """Detect suspicious usage patterns."""
        try:
            # Check for rapid request bursts
            if 'request_timestamps' in key_info:
                recent_requests = [t for t in key_info['request_timestamps'] 
                                 if (datetime.now() - t).total_seconds() < 60]
                if len(recent_requests) > self.alert_thresholds['rate_limit']:
                    return True
                    
            # Check for concurrent requests
            if key_info.get('concurrent_requests', 0) > self.alert_thresholds['concurrent_limit']:
                return True
                
            # Check for unusual request patterns
            if 'request_patterns' in key_info:
                pattern = key_info['request_patterns'][-10:]  # Last 10 requests
                if len(set(pattern)) == 1:  # All requests are identical
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting suspicious patterns: {str(e)}")
            return False

    def get_usage_alert(self, api_key: str) -> Optional[str]:
        """Get usage alert message if thresholds are exceeded."""
        try:
            if api_key not in self.api_keys:
                return None
                
            key_info = self.api_keys[api_key]
            tier_limit = self.usage_limits[key_info['tier']]
            current_usage = key_info.get('usage_count', 0)
            usage_percentage = current_usage / tier_limit
            
            if usage_percentage >= self.alert_thresholds['usage_critical']:
                return f"Critical: API usage at {usage_percentage:.1%} of limit"
            elif usage_percentage >= self.alert_thresholds['usage_warning']:
                return f"Warning: API usage at {usage_percentage:.1%} of limit"
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting usage alert: {str(e)}")
            return None 