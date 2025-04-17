"""
Schema definitions and validation for healthcare data.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum

class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

class AdmissionType(str, Enum):
    """Admission type enumeration."""
    EMERGENCY = "emergency"
    ELECTIVE = "elective"
    URGENT = "urgent"
    OBSERVATION = "observation"

class Patient(BaseModel):
    """Patient data model."""
    patient_id: str = Field(..., pattern=r'^P\d+$')
    birth_date: date
    gender: Gender
    race: str
    ethnicity: str
    insurance_id: str = None
    risk_score: float = None

    class Config:
        schema_extra = {
            "example": {
                "patient_id": "P12345",
                "birth_date": "1980-01-01",
                "gender": "M",
                "race": "White",
                "ethnicity": "Non-Hispanic",
                "insurance_id": "INS789",
                "risk_score": 0.35
            }
        }

class Encounter(BaseModel):
    """Encounter/visit data model."""
    encounter_id: str = Field(..., pattern=r'^E\d+$')
    patient_id: str = Field(..., pattern=r'^P\d+$')
    admission_date: datetime
    discharge_date: datetime = None
    admission_type: AdmissionType
    diagnosis_codes: List[str]
    length_of_stay: float = None
    total_cost: float = None

    @validator('discharge_date')
    def discharge_after_admission(cls, v, values):
        """Validate discharge date is after admission date."""
        if v and 'admission_date' in values and v < values['admission_date']:
            raise ValueError('Discharge date must be after admission date')
        return v

    class Config:
        schema_extra = {
            "example": {
                "encounter_id": "E12345",
                "patient_id": "P12345",
                "admission_date": "2023-01-01T10:00:00",
                "discharge_date": "2023-01-05T14:30:00",
                "admission_type": "emergency",
                "diagnosis_codes": ["I21.0", "E11.9"],
                "length_of_stay": 4.5,
                "total_cost": 12500.00
            }
        }

class LabResult(BaseModel):
    """Laboratory result data model."""
    lab_result_id: str = Field(..., pattern=r'^L\d+$')
    patient_id: str = Field(..., pattern=r'^P\d+$')
    encounter_id: str = Field(..., pattern=r'^E\d+$')
    lab_test_code: str
    result_date: datetime
    result_value: float
    unit: str
    reference_range_low: float = None
    reference_range_high: float = None
    is_abnormal: bool = None

    @validator('is_abnormal', always=True)
    def calculate_abnormal(cls, v, values):
        """Calculate if result is abnormal based on reference range."""
        if v is not None:
            return v
        
        if all(k in values for k in ['result_value', 'reference_range_low', 'reference_range_high']):
            if values['reference_range_low'] is not None and values['reference_range_high'] is not None:
                return (
                    values['result_value'] < values['reference_range_low'] or
                    values['result_value'] > values['reference_range_high']
                )
        return None

    class Config:
        schema_extra = {
            "example": {
                "lab_result_id": "L12345",
                "patient_id": "P12345",
                "encounter_id": "E12345",
                "lab_test_code": "CBC",
                "result_date": "2023-01-02T11:30:00",
                "result_value": 14.5,
                "unit": "g/dL",
                "reference_range_low": 12.0,
                "reference_range_high": 16.0,
                "is_abnormal": False
            }
        }

class RiskPrediction(BaseModel):
    """Risk prediction model output."""
    patient_id: str = Field(..., pattern=r'^P\d+$')
    prediction_date: datetime
    risk_score: float = Field(..., ge=0, le=1)
    risk_factors: List[Dict[str, float]]
    confidence: float = Field(..., ge=0, le=1)
    next_review_date: datetime = None

    class Config:
        schema_extra = {
            "example": {
                "patient_id": "P12345",
                "prediction_date": "2023-01-01T00:00:00",
                "risk_score": 0.75,
                "risk_factors": [
                    {"age": 0.3},
                    {"previous_admissions": 0.25},
                    {"comorbidities": 0.2}
                ],
                "confidence": 0.85,
                "next_review_date": "2023-01-08T00:00:00"
            }
        }

class LengthOfStayPrediction(BaseModel):
    """Length of stay prediction model output."""
    encounter_id: str = Field(..., pattern=r'^E\d+$')
    prediction_date: datetime
    predicted_los: float = Field(..., ge=0)
    confidence_interval: Dict[str, float]
    contributing_factors: List[Dict[str, float]]

    class Config:
        schema_extra = {
            "example": {
                "encounter_id": "E12345",
                "prediction_date": "2023-01-01T00:00:00",
                "predicted_los": 5.2,
                "confidence_interval": {
                    "lower": 4.5,
                    "upper": 6.0
                },
                "contributing_factors": [
                    {"diagnosis_severity": 0.4},
                    {"age": 0.3},
                    {"comorbidities": 0.3}
                ]
            }
        } 