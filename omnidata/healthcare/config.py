"""
Configuration settings for healthcare domain.
"""

from typing import Dict, Any
from pathlib import Path
import yaml
import os

# Model Configuration
MODEL_CONFIG = {
    "readmission_risk": {
        "features": [
            "age",
            "gender_code",
            "num_diagnoses",
            "previous_admissions",
            "emergency_admission",
            "length_of_stay",
            "lab_result_count",
            "avg_lab_mean",
            "avg_lab_std"
        ],
        "hyperparameters": {
            "max_depth": 8,
            "learning_rate": 0.05,
            "n_estimators": 200,
            "min_child_weight": 1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "binary:logistic",
            "eval_metric": "auc"
        },
        "training": {
            "test_size": 0.2,
            "random_state": 42,
            "early_stopping_rounds": 10
        }
    },
    "length_of_stay": {
        "features": [
            "age",
            "gender_code",
            "num_diagnoses",
            "admission_type",
            "emergency_admission",
            "previous_admissions",
            "lab_result_count",
            "avg_lab_mean",
            "avg_lab_std"
        ],
        "hyperparameters": {
            "num_leaves": 31,
            "learning_rate": 0.05,
            "n_estimators": 150,
            "min_child_samples": 20,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "regression",
            "metric": "rmse"
        },
        "training": {
            "test_size": 0.2,
            "random_state": 42,
            "early_stopping_rounds": 10
        }
    }
}

# Data Processing Configuration
PROCESSING_CONFIG = {
    "patient_data": {
        "required_columns": [
            "patient_id",
            "birth_date",
            "gender",
            "race",
            "ethnicity"
        ],
        "date_columns": ["birth_date"],
        "categorical_columns": ["gender", "race", "ethnicity"],
        "id_columns": ["patient_id"]
    },
    "encounter_data": {
        "required_columns": [
            "encounter_id",
            "patient_id",
            "admission_date",
            "discharge_date",
            "admission_type",
            "diagnosis_codes"
        ],
        "date_columns": ["admission_date", "discharge_date"],
        "categorical_columns": ["admission_type"],
        "id_columns": ["encounter_id", "patient_id"]
    },
    "lab_results": {
        "required_columns": [
            "lab_result_id",
            "patient_id",
            "encounter_id",
            "lab_test_code",
            "result_date",
            "result_value"
        ],
        "date_columns": ["result_date"],
        "categorical_columns": ["lab_test_code"],
        "id_columns": ["lab_result_id", "patient_id", "encounter_id"]
    }
}

# Feature Engineering Configuration
FEATURE_CONFIG = {
    "temporal_features": {
        "lookback_periods": [30, 90, 180, 365],  # days
        "aggregation_functions": ["mean", "max", "sum", "count"]
    },
    "diagnosis_features": {
        "max_codes": 10,  # Maximum number of diagnosis codes to consider
        "code_type": "icd10",  # ICD-10 coding system
        "grouping_level": "category"  # Options: category, subcategory, code
    },
    "lab_features": {
        "trend_window": 7,  # days
        "missing_threshold": 0.5,  # Maximum allowed missing values
        "outlier_std": 3  # Standard deviations for outlier detection
    }
}

# Validation Rules
VALIDATION_RULES = {
    "age": {
        "min": 0,
        "max": 120
    },
    "length_of_stay": {
        "min": 0,
        "max": 365
    },
    "lab_values": {
        "outlier_detection": "iqr",  # Options: iqr, zscore, none
        "iqr_multiplier": 1.5
    }
}

# Risk Score Thresholds
RISK_THRESHOLDS = {
    "readmission": {
        "low": 0.3,
        "medium": 0.6,
        "high": 0.8
    },
    "length_of_stay": {
        "short": 3,  # days
        "medium": 7,
        "long": 14
    }
}

class HealthcareConfig:
    """Healthcare configuration manager."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration."""
        self.config_path = config_path
        self.config = {
            "models": MODEL_CONFIG,
            "processing": PROCESSING_CONFIG,
            "features": FEATURE_CONFIG,
            "validation": VALIDATION_RULES,
            "thresholds": RISK_THRESHOLDS
        }
        
        if config_path:
            self._load_custom_config()
    
    def _load_custom_config(self) -> None:
        """Load custom configuration from file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            custom_config = yaml.safe_load(f)
            
        # Update configuration with custom settings
        for section, values in custom_config.items():
            if section in self.config:
                self.config[section].update(values)
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for specific model."""
        if model_name not in self.config["models"]:
            raise ValueError(f"Unknown model: {model_name}")
        return self.config["models"][model_name]
    
    def get_processing_config(self, data_type: str) -> Dict[str, Any]:
        """Get configuration for data processing."""
        if data_type not in self.config["processing"]:
            raise ValueError(f"Unknown data type: {data_type}")
        return self.config["processing"][data_type]
    
    def get_feature_config(self) -> Dict[str, Any]:
        """Get feature engineering configuration."""
        return self.config["features"]
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get data validation rules."""
        return self.config["validation"]
    
    def get_risk_thresholds(self) -> Dict[str, Any]:
        """Get risk score thresholds."""
        return self.config["thresholds"]
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update configuration value."""
        if section not in self.config:
            raise ValueError(f"Unknown configuration section: {section}")
        
        if isinstance(self.config[section], dict):
            self.config[section][key] = value
        else:
            raise ValueError(f"Cannot update non-dict section: {section}")
    
    def save_config(self, output_path: str) -> None:
        """Save current configuration to file."""
        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False) 