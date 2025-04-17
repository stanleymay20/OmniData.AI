"""
Test module for healthcare models and processors.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from omnidata.healthcare.models import ReadmissionRiskModel, LengthOfStayModel
from omnidata.healthcare.processors import ClinicalDataProcessor

class TestClinicalDataProcessor(unittest.TestCase):
    """Test cases for ClinicalDataProcessor."""
    
    def setUp(self):
        """Set up test data and processor instance."""
        self.config = {
            "schemas": {
                "patients": None,  # Schema validation disabled for testing
                "encounters": None,
                "lab_results": None
            }
        }
        self.processor = ClinicalDataProcessor(self.config, schema_validation=False)
        
        # Create sample patient data
        self.patient_data = pd.DataFrame({
            "patient_id": ["P001", "P002", "P003"],
            "birth_date": ["1980-01-01", "1990-01-01", "2000-01-01"],
            "gender": ["M", "F", "O"],
            "race": ["White", "Asian", "Black"],
            "ethnicity": ["Hispanic", "Non-Hispanic", "Hispanic"]
        })
        
        # Create sample encounter data
        self.encounter_data = pd.DataFrame({
            "encounter_id": ["E001", "E002", "E003"],
            "patient_id": ["P001", "P001", "P002"],
            "admission_date": ["2023-01-01", "2023-02-01", "2023-01-15"],
            "discharge_date": ["2023-01-05", "2023-02-05", "2023-01-20"],
            "admission_type": ["Emergency", "Elective", "Emergency"],
            "diagnosis_codes": ['["A01", "B02"]', '["C03"]', '["D04", "E05", "F06"]']
        })
        
        # Create sample lab data
        self.lab_data = pd.DataFrame({
            "lab_result_id": ["L001", "L002", "L003", "L004"],
            "patient_id": ["P001", "P001", "P002", "P002"],
            "encounter_id": ["E001", "E001", "E002", "E002"],
            "lab_test_code": ["CBC", "CBC", "BMP", "BMP"],
            "result_date": ["2023-01-02", "2023-01-03", "2023-01-16", "2023-01-17"],
            "result_value": ["10.5", "11.0", "140", "138"]
        })

    def test_process_patient_data(self):
        """Test patient data processing."""
        processed = self.processor.process_patient_data(self.patient_data)
        
        # Check age calculation
        self.assertTrue("age" in processed.columns)
        self.assertEqual(len(processed), len(self.patient_data))
        
        # Check gender encoding
        self.assertTrue("gender_code" in processed.columns)
        self.assertEqual(processed.loc[0, "gender_code"], 1)  # M = 1
        self.assertEqual(processed.loc[1, "gender_code"], 0)  # F = 0
        
        # Check race/ethnicity encoding
        self.assertTrue(any(col.startswith("race_") for col in processed.columns))
        self.assertTrue(any(col.startswith("ethnicity_") for col in processed.columns))

    def test_process_encounters(self):
        """Test encounter data processing."""
        processed = self.processor.process_encounters(self.encounter_data)
        
        # Check length of stay calculation
        self.assertTrue("length_of_stay" in processed.columns)
        self.assertEqual(processed.loc[0, "length_of_stay"], 4.0)  # 5 - 1 = 4 days
        
        # Check diagnosis code processing
        self.assertTrue("primary_diagnosis_code" in processed.columns)
        self.assertTrue("diagnosis_count" in processed.columns)
        self.assertEqual(processed.loc[0, "diagnosis_count"], 2)
        
        # Check admission type encoding
        self.assertTrue(any(col.startswith("adm_") for col in processed.columns))

    def test_process_lab_results(self):
        """Test lab results processing."""
        processed = self.processor.process_lab_results(self.lab_data)
        
        # Check numeric conversion
        self.assertTrue("result_value_numeric" in processed.columns)
        
        # Check trend calculations
        self.assertTrue("lab_mean" in processed.columns)
        self.assertTrue("lab_std" in processed.columns)
        self.assertTrue("lab_count" in processed.columns)

    def test_generate_features(self):
        """Test feature generation."""
        features = self.processor.generate_features(
            self.patient_data,
            self.encounter_data,
            self.lab_data
        )
        
        # Check required features
        required_features = [
            "encounter_count",
            "avg_los",
            "total_diagnoses",
            "lab_result_count",
            "avg_lab_mean"
        ]
        for feature in required_features:
            self.assertTrue(feature in features.columns)
        
        # Check aggregations
        self.assertEqual(features.loc[0, "encounter_count"], 2)  # P001 has 2 encounters

    def test_extract_readmissions(self):
        """Test readmission extraction."""
        readmissions = self.processor.extract_readmissions(self.encounter_data)
        
        # Check required columns
        required_columns = [
            "encounter_id",
            "patient_id",
            "admission_date",
            "discharge_date",
            "days_to_readmission",
            "is_readmission"
        ]
        for column in required_columns:
            self.assertTrue(column in readmissions.columns)
        
        # Check readmission flagging
        self.assertTrue("is_readmission" in readmissions.columns)

class TestHealthcareModels(unittest.TestCase):
    """Test cases for healthcare ML models."""
    
    def setUp(self):
        """Set up test data and model instances."""
        # Create sample features and target
        np.random.seed(42)
        n_samples = 1000
        
        self.features = pd.DataFrame({
            "age": np.random.normal(65, 15, n_samples),
            "gender_code": np.random.choice([0, 1], n_samples),
            "num_diagnoses": np.random.poisson(3, n_samples),
            "previous_admissions": np.random.poisson(2, n_samples),
            "emergency_admission": np.random.choice([0, 1], n_samples)
        })
        
        # Create readmission target (classification)
        self.readmission_target = (
            0.3 * self.features["previous_admissions"] +
            0.2 * self.features["emergency_admission"] +
            0.1 * (self.features["age"] > 70)
        )
        self.readmission_target = (self.readmission_target + np.random.normal(0, 0.1, n_samples) > 1).astype(int)
        
        # Create length of stay target (regression)
        self.los_target = (
            2 * self.features["num_diagnoses"] +
            1.5 * self.features["emergency_admission"] +
            0.05 * self.features["age"]
        )
        self.los_target = self.los_target + np.random.normal(0, 1, n_samples)
        
        # Initialize models
        self.readmission_model = ReadmissionRiskModel(
            features=list(self.features.columns)
        )
        
        self.los_model = LengthOfStayModel(
            features=list(self.features.columns)
        )

    def test_readmission_model(self):
        """Test readmission risk model."""
        # Train model
        train_result = self.readmission_model.train(
            self.features,
            target="readmission",
            test_size=0.2
        )
        
        # Check training success
        self.assertEqual(train_result["status"], "success")
        self.assertTrue("metrics" in train_result)
        self.assertTrue("train_auc" in train_result["metrics"])
        self.assertTrue("test_auc" in train_result["metrics"])
        
        # Test predictions
        pred_result = self.readmission_model.predict(self.features.head())
        self.assertEqual(pred_result["status"], "success")
        self.assertTrue("risk_scores" in pred_result["predictions"])

    def test_los_model(self):
        """Test length of stay model."""
        # Train model
        train_result = self.los_model.train(
            self.features,
            target="length_of_stay",
            test_size=0.2
        )
        
        # Check training success
        self.assertEqual(train_result["status"], "success")
        self.assertTrue("metrics" in train_result)
        self.assertTrue("train_rmse" in train_result["metrics"])
        self.assertTrue("test_rmse" in train_result["metrics"])
        
        # Test predictions
        pred_result = self.los_model.predict(self.features.head())
        self.assertEqual(pred_result["status"], "success")
        self.assertTrue("los_predictions" in pred_result["predictions"])

if __name__ == "__main__":
    unittest.main() 