"""
ScrollIntel v2: The Flame Interpreter
Data sanctification and integrity verification engine
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

class ScrollSanctify:
    """Data sanctification and integrity verification engine."""
    
    def __init__(self):
        self.breach_messages = {
            "missing": "⚠️ Scroll breach detected: incomplete records",
            "bias": "⚠️ Scroll breach detected: unjust distribution",
            "corruption": "⚠️ Scroll breach detected: corrupted data",
            "anomaly": "⚠️ Scroll breach detected: anomalous patterns",
            "inconsistency": "⚠️ Scroll breach detected: inconsistent records"
        }
    
    def sanctify_data(
        self,
        data: pd.DataFrame,
        domain: str,
        sacred_timing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive data sanctification checks."""
        try:
            # Initialize results
            results = {
                "is_sanctified": True,
                "breaches": [],
                "warnings": [],
                "metrics": {},
                "timestamp": datetime.now(pytz.UTC).isoformat(),
                "sacred_timing": sacred_timing
            }
            
            # Check for missing values
            missing_check = self._check_missing_values(data)
            if not missing_check["is_valid"]:
                results["is_sanctified"] = False
                results["breaches"].append({
                    "type": "missing",
                    "message": self.breach_messages["missing"],
                    "details": missing_check["details"]
                })
            
            # Check for bias
            bias_check = self._check_bias(data)
            if not bias_check["is_valid"]:
                results["is_sanctified"] = False
                results["breaches"].append({
                    "type": "bias",
                    "message": self.breach_messages["bias"],
                    "details": bias_check["details"]
                })
            
            # Check for corruption
            corruption_check = self._check_corruption(data)
            if not corruption_check["is_valid"]:
                results["is_sanctified"] = False
                results["breaches"].append({
                    "type": "corruption",
                    "message": self.breach_messages["corruption"],
                    "details": corruption_check["details"]
                })
            
            # Check for anomalies
            anomaly_check = self._check_anomalies(data)
            if not anomaly_check["is_valid"]:
                results["warnings"].append({
                    "type": "anomaly",
                    "message": self.breach_messages["anomaly"],
                    "details": anomaly_check["details"]
                })
            
            # Check for consistency
            consistency_check = self._check_consistency(data)
            if not consistency_check["is_valid"]:
                results["warnings"].append({
                    "type": "inconsistency",
                    "message": self.breach_messages["inconsistency"],
                    "details": consistency_check["details"]
                })
            
            # Calculate sanctification metrics
            results["metrics"] = self._calculate_sanctification_metrics(
                data,
                results["breaches"],
                results["warnings"]
            )
            
            return results
        except Exception as e:
            raise ValueError(f"Data sanctification failed: {str(e)}")
    
    def _check_missing_values(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values in the dataset."""
        missing = data.isnull().sum()
        missing_pct = (missing / len(data)) * 100
        
        return {
            "is_valid": missing_pct.max() < 5.0,  # Allow up to 5% missing
            "details": {
                "missing_counts": missing.to_dict(),
                "missing_percentages": missing_pct.to_dict()
            }
        }
    
    def _check_bias(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for bias in the dataset."""
        bias_results = {}
        
        for column in data.select_dtypes(include=[np.number]).columns:
            # Calculate distribution metrics
            mean = data[column].mean()
            median = data[column].median()
            std = data[column].std()
            
            # Check for significant skew
            skew = abs(mean - median) / std if std > 0 else 0
            
            bias_results[column] = {
                "skew": skew,
                "is_biased": skew > 2.0  # Consider biased if skew > 2
            }
        
        return {
            "is_valid": not any(result["is_biased"] for result in bias_results.values()),
            "details": bias_results
        }
    
    def _check_corruption(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for data corruption."""
        corruption_results = {}
        
        for column in data.select_dtypes(include=[np.number]).columns:
            # Check for infinite values
            inf_count = np.isinf(data[column]).sum()
            
            # Check for extreme outliers
            q1 = data[column].quantile(0.25)
            q3 = data[column].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 3 * iqr
            upper_bound = q3 + 3 * iqr
            outliers = ((data[column] < lower_bound) | (data[column] > upper_bound)).sum()
            
            corruption_results[column] = {
                "inf_count": inf_count,
                "outlier_count": outliers,
                "is_corrupted": inf_count > 0 or outliers > len(data) * 0.1
            }
        
        return {
            "is_valid": not any(result["is_corrupted"] for result in corruption_results.values()),
            "details": corruption_results
        }
    
    def _check_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for anomalous patterns."""
        anomaly_results = {}
        
        for column in data.select_dtypes(include=[np.number]).columns:
            # Calculate z-scores
            z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
            anomalies = (z_scores > 3).sum()  # Values more than 3 standard deviations
            
            anomaly_results[column] = {
                "anomaly_count": anomalies,
                "has_anomalies": anomalies > 0
            }
        
        return {
            "is_valid": not any(result["has_anomalies"] for result in anomaly_results.values()),
            "details": anomaly_results
        }
    
    def _check_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for data consistency."""
        consistency_results = {}
        
        for column in data.select_dtypes(include=[np.number]).columns:
            # Check for sudden changes
            changes = data[column].diff().abs()
            sudden_changes = (changes > changes.mean() + 3 * changes.std()).sum()
            
            consistency_results[column] = {
                "sudden_changes": sudden_changes,
                "is_inconsistent": sudden_changes > len(data) * 0.05
            }
        
        return {
            "is_valid": not any(result["is_inconsistent"] for result in consistency_results.values()),
            "details": consistency_results
        }
    
    def _calculate_sanctification_metrics(
        self,
        data: pd.DataFrame,
        breaches: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall sanctification metrics."""
        total_checks = 5  # Number of different checks performed
        passed_checks = total_checks - len(breaches)
        
        return {
            "sanctification_score": (passed_checks / total_checks) * 100,
            "breach_count": len(breaches),
            "warning_count": len(warnings),
            "data_quality": {
                "completeness": (1 - data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100,
                "consistency": 100 - (len(warnings) / total_checks) * 100,
                "integrity": 100 - (len(breaches) / total_checks) * 100
            }
        } 