"""
ScrollIntel v2: The Flame Interpreter
Base integration module
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import pytz
import logging
import json
import os

class BaseIntegration(ABC):
    """Base class for all ScrollIntel integrations."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """Initialize integration with credentials."""
        self.credentials = credentials
        self.logger = logging.getLogger(f"scrollintel.integrations.{self.__class__.__name__}")
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging for the integration."""
        log_dir = "logs/integrations"
        os.makedirs(log_dir, exist_ok=True)
        
        handler = logging.FileHandler(
            f"{log_dir}/{self.__class__.__name__}.log"
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _log_integration(self, action: str, details: Dict[str, Any]):
        """Log integration activity."""
        log_entry = {
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "integration": self.__class__.__name__,
            "action": action,
            "details": details
        }
        self.logger.info(json.dumps(log_entry))
    
    def _sanitize_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize credentials for logging."""
        sanitized = credentials.copy()
        for key in sanitized:
            if any(sensitive in key.lower() for sensitive in ["key", "token", "secret", "password"]):
                sanitized[key] = "***"
        return sanitized
    
    @abstractmethod
    async def fetch_data(
        self,
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Fetch data from the integration source."""
        pass
    
    @abstractmethod
    async def list_resources(
        self,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List available resources in the integration."""
        pass
    
    @abstractmethod
    async def get_resource_info(
        self,
        resource_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get information about a specific resource."""
        pass
    
    def to_dataframe(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]]
    ) -> pd.DataFrame:
        """Convert data to pandas DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def validate_credentials(self) -> bool:
        """Validate integration credentials."""
        try:
            self._log_integration(
                "validate_credentials",
                {"credentials": self._sanitize_credentials(self.credentials)}
            )
            return True
        except Exception as e:
            self.logger.error(f"Credential validation failed: {str(e)}")
            return False 