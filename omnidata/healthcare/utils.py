"""
Utility functions for healthcare data processing and validation.
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

def validate_patient_identifiers(data: pd.DataFrame) -> bool:
    """Validate patient identifier format and uniqueness."""
    if "patient_id" not in data.columns:
        return False
    
    # Check format (e.g., P followed by numbers)
    valid_format = data["patient_id"].str.match(r'^P\d+$').all()
    
    # Check uniqueness
    is_unique = data["patient_id"].is_unique
    
    return valid_format and is_unique

def validate_date_ranges(
    data: pd.DataFrame,
    date_column: str,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None
) -> bool:
    """Validate date ranges in data."""
    if date_column not in data.columns:
        return False
    
    dates = pd.to_datetime(data[date_column], errors='coerce')
    
    # Check for invalid dates
    if dates.isna().any():
        return False
    
    # Check min date if specified
    if min_date and (dates < pd.to_datetime(min_date)).any():
        return False
    
    # Check max date if specified
    if max_date and (dates > pd.to_datetime(max_date)).any():
        return False
    
    return True

def calculate_age(
    birth_date: Union[str, pd.Series],
    reference_date: Optional[str] = None
) -> Union[float, pd.Series]:
    """Calculate age from birth date."""
    if reference_date is None:
        reference_date = datetime.now()
    else:
        reference_date = pd.to_datetime(reference_date)
    
    birth_date = pd.to_datetime(birth_date)
    age = (reference_date - birth_date).dt.total_days() / 365.25
    
    return age

def parse_icd_codes(
    codes: Union[str, List[str]],
    code_type: str = "icd10"
) -> List[str]:
    """Parse and validate ICD diagnosis codes."""
    if isinstance(codes, str):
        try:
            codes = json.loads(codes)
        except json.JSONDecodeError:
            codes = [codes]
    
    # Validate code format
    if code_type == "icd10":
        pattern = r'^[A-Z]\d{2}(\.\d{1,2})?$'
    else:  # icd9
        pattern = r'^\d{3}(\.\d{1,2})?$'
    
    import re
    valid_codes = [
        code for code in codes
        if re.match(pattern, code.strip())
    ]
    
    return valid_codes

def calculate_charlson_index(diagnosis_codes: List[str]) -> int:
    """Calculate Charlson Comorbidity Index."""
    # Mapping of ICD-10 codes to Charlson conditions and weights
    charlson_map = {
        "myocardial_infarction": {
            "codes": ["I21", "I22", "I25.2"],
            "weight": 1
        },
        "congestive_heart_failure": {
            "codes": ["I09.9", "I11.0", "I13.0", "I13.2", "I25.5", "I42", "I43", "I50"],
            "weight": 1
        },
        # Add more conditions...
    }
    
    score = 0
    for code in diagnosis_codes:
        for condition in charlson_map.values():
            if any(code.startswith(c) for c in condition["codes"]):
                score += condition["weight"]
                break
    
    return score

def detect_lab_anomalies(
    data: pd.DataFrame,
    value_column: str,
    method: str = "iqr",
    threshold: float = 1.5
) -> pd.Series:
    """Detect anomalies in lab results."""
    if method == "iqr":
        Q1 = data[value_column].quantile(0.25)
        Q3 = data[value_column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        return (data[value_column] < lower_bound) | (data[value_column] > upper_bound)
    
    elif method == "zscore":
        z_scores = (data[value_column] - data[value_column].mean()) / data[value_column].std()
        return abs(z_scores) > threshold
    
    else:
        raise ValueError(f"Unknown anomaly detection method: {method}")

def calculate_lab_trends(
    data: pd.DataFrame,
    value_column: str,
    date_column: str,
    window: str = "7D"
) -> Dict[str, pd.Series]:
    """Calculate trends in lab results."""
    # Sort by date
    data = data.sort_values(date_column)
    
    # Calculate rolling statistics
    rolling = data[value_column].rolling(window=window)
    
    trends = {
        "mean": rolling.mean(),
        "std": rolling.std(),
        "min": rolling.min(),
        "max": rolling.max(),
        "slope": calculate_slope(data[value_column], data[date_column])
    }
    
    return trends

def calculate_slope(
    values: pd.Series,
    dates: pd.Series
) -> float:
    """Calculate slope of trend line."""
    x = (pd.to_datetime(dates) - pd.to_datetime(dates.iloc[0])).dt.total_seconds()
    y = values
    
    if len(x) < 2:
        return 0.0
    
    slope, _ = np.polyfit(x, y, 1)
    return slope

def format_timedelta(td: timedelta) -> str:
    """Format timedelta into human-readable string."""
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "0m"

def anonymize_patient_data(
    data: pd.DataFrame,
    columns_to_hash: List[str]
) -> pd.DataFrame:
    """Anonymize sensitive patient information."""
    from hashlib import sha256
    
    anonymized = data.copy()
    
    for column in columns_to_hash:
        if column in data.columns:
            anonymized[column] = data[column].apply(
                lambda x: sha256(str(x).encode()).hexdigest()
            )
    
    return anonymized
