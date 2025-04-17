"""
Healthcare data processing and ETL functionality for OmniData.AI
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from omnidata.core.base import DataProcessor
from omnidata.core.utils import validate_schema

class ClinicalDataProcessor(DataProcessor):
    """Processes clinical data for healthcare analytics."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        schema_validation: bool = True
    ):
        super().__init__(config)
        self.schema_validation = schema_validation
        self.icd_codes_map = {}  # Cache for ICD code lookups
        
    def process_patient_data(
        self,
        data: pd.DataFrame,
        include_demographics: bool = True
    ) -> pd.DataFrame:
        """Process patient-level data."""
        if self.schema_validation:
            validate_schema(data, self.config["schemas"]["patients"])
        
        processed_data = data.copy()
        
        if include_demographics:
            # Calculate age from birth date
            processed_data["age"] = (
                pd.Timestamp.now() - pd.to_datetime(processed_data["birth_date"])
            ).dt.total_days() / 365.25
            
            # Encode gender
            processed_data["gender_code"] = processed_data["gender"].map({
                "M": 1, "F": 0, "O": 2
            })
            
            # Process race and ethnicity
            processed_data = pd.get_dummies(
                processed_data,
                columns=["race", "ethnicity"],
                prefix=["race", "ethnicity"]
            )
        
        # Clean and standardize identifiers
        processed_data["patient_id"] = processed_data["patient_id"].astype(str)
        
        return processed_data
    
    def process_encounters(
        self,
        data: pd.DataFrame,
        calculate_los: bool = True
    ) -> pd.DataFrame:
        """Process encounter/visit data."""
        if self.schema_validation:
            validate_schema(data, self.config["schemas"]["encounters"])
        
        processed_data = data.copy()
        
        # Convert timestamps
        processed_data["admission_date"] = pd.to_datetime(processed_data["admission_date"])
        processed_data["discharge_date"] = pd.to_datetime(processed_data["discharge_date"])
        
        if calculate_los:
            # Calculate length of stay
            processed_data["length_of_stay"] = (
                processed_data["discharge_date"] - processed_data["admission_date"]
            ).dt.total_days()
        
        # Process admission type
        processed_data = pd.get_dummies(
            processed_data,
            columns=["admission_type"],
            prefix=["adm"]
        )
        
        # Process diagnosis codes
        processed_data["primary_diagnosis_code"] = processed_data["diagnosis_codes"].apply(
            lambda x: json.loads(x)[0] if isinstance(x, str) else x[0]
        )
        processed_data["diagnosis_count"] = processed_data["diagnosis_codes"].apply(
            lambda x: len(json.loads(x)) if isinstance(x, str) else len(x)
        )
        
        # Clean identifiers
        processed_data["encounter_id"] = processed_data["encounter_id"].astype(str)
        processed_data["patient_id"] = processed_data["patient_id"].astype(str)
        
        return processed_data
    
    def process_lab_results(
        self,
        data: pd.DataFrame,
        include_trends: bool = True
    ) -> pd.DataFrame:
        """Process laboratory results data."""
        if self.schema_validation:
            validate_schema(data, self.config["schemas"]["lab_results"])
        
        processed_data = data.copy()
        
        # Convert timestamps
        processed_data["result_date"] = pd.to_datetime(processed_data["result_date"])
        
        # Normalize numeric results
        processed_data["result_value_numeric"] = pd.to_numeric(
            processed_data["result_value"],
            errors="coerce"
        )
        
        if include_trends:
            # Calculate trends per patient and lab test
            trends = processed_data.groupby(
                ["patient_id", "lab_test_code"]
            ).agg({
                "result_value_numeric": [
                    "mean",
                    "std",
                    "min",
                    "max",
                    "count"
                ]
            }).reset_index()
            
            trends.columns = [
                "patient_id",
                "lab_test_code",
                "lab_mean",
                "lab_std",
                "lab_min",
                "lab_max",
                "lab_count"
            ]
            
            processed_data = processed_data.merge(
                trends,
                on=["patient_id", "lab_test_code"],
                how="left"
            )
        
        # Clean identifiers
        processed_data["lab_result_id"] = processed_data["lab_result_id"].astype(str)
        processed_data["patient_id"] = processed_data["patient_id"].astype(str)
        processed_data["encounter_id"] = processed_data["encounter_id"].astype(str)
        
        return processed_data
    
    def generate_features(
        self,
        patient_data: pd.DataFrame,
        encounter_data: pd.DataFrame,
        lab_data: pd.DataFrame,
        lookback_days: int = 365
    ) -> pd.DataFrame:
        """Generate features for ML models."""
        # Process each data type
        patients = self.process_patient_data(patient_data)
        encounters = self.process_encounters(encounter_data)
        labs = self.process_lab_results(lab_data)
        
        # Set reference date for temporal features
        reference_date = encounters["admission_date"].max()
        
        # Filter data within lookback period
        lookback_date = reference_date - pd.Timedelta(days=lookback_days)
        encounters_lookback = encounters[
            encounters["admission_date"] >= lookback_date
        ]
        labs_lookback = labs[
            labs["result_date"] >= lookback_date
        ]
        
        # Aggregate encounter history
        encounter_features = encounters_lookback.groupby("patient_id").agg({
            "encounter_id": "count",
            "length_of_stay": ["mean", "max", "sum"],
            "diagnosis_count": ["mean", "max", "sum"]
        }).reset_index()
        
        encounter_features.columns = [
            "patient_id",
            "encounter_count",
            "avg_los",
            "max_los",
            "total_los",
            "avg_diagnoses",
            "max_diagnoses",
            "total_diagnoses"
        ]
        
        # Aggregate lab history
        lab_features = labs_lookback.groupby("patient_id").agg({
            "lab_result_id": "count",
            "lab_mean": "mean",
            "lab_std": "mean",
            "lab_count": "sum"
        }).reset_index()
        
        lab_features.columns = [
            "patient_id",
            "lab_result_count",
            "avg_lab_mean",
            "avg_lab_std",
            "total_lab_tests"
        ]
        
        # Combine all features
        features = patients.merge(
            encounter_features,
            on="patient_id",
            how="left"
        ).merge(
            lab_features,
            on="patient_id",
            how="left"
        )
        
        # Fill missing values
        features = features.fillna({
            "encounter_count": 0,
            "avg_los": 0,
            "max_los": 0,
            "total_los": 0,
            "avg_diagnoses": 0,
            "max_diagnoses": 0,
            "total_diagnoses": 0,
            "lab_result_count": 0,
            "avg_lab_mean": 0,
            "avg_lab_std": 0,
            "total_lab_tests": 0
        })
        
        return features
    
    def extract_readmissions(
        self,
        encounter_data: pd.DataFrame,
        window_days: int = 30
    ) -> pd.DataFrame:
        """Extract readmission events for training data."""
        encounters = self.process_encounters(encounter_data)
        
        # Sort encounters by patient and date
        encounters = encounters.sort_values(
            ["patient_id", "admission_date"]
        )
        
        # Calculate days until next admission
        encounters["next_admission"] = encounters.groupby("patient_id")["admission_date"].shift(-1)
        encounters["days_to_readmission"] = (
            encounters["next_admission"] - encounters["discharge_date"]
        ).dt.total_days()
        
        # Flag readmissions within window
        encounters["is_readmission"] = (
            encounters["days_to_readmission"] <= window_days
        ).astype(int)
        
        return encounters[
            [
                "encounter_id",
                "patient_id",
                "admission_date",
                "discharge_date",
                "days_to_readmission",
                "is_readmission"
            ]
        ] 