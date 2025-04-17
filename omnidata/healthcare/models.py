"""
Healthcare ML Models for OmniData.AI
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import lightgbm as lgb
from omnidata.scientist.automl import AutoML

class ReadmissionRiskModel:
    """Predicts patient readmission risk."""
    
    def __init__(
        self,
        features: List[str],
        hyperparameters: Optional[Dict[str, Any]] = None
    ):
        self.features = features
        self.hyperparameters = hyperparameters or {
            "max_depth": 8,
            "learning_rate": 0.05,
            "n_estimators": 200
        }
        self.model = None
        self.feature_preprocessors = {}
        
    def preprocess_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess features for model input."""
        processed_data = data.copy()
        
        # Handle categorical features
        categorical_features = data.select_dtypes(include=['object']).columns
        for feature in categorical_features:
            if feature not in self.feature_preprocessors:
                self.feature_preprocessors[feature] = LabelEncoder()
            processed_data[feature] = self.feature_preprocessors[feature].fit_transform(data[feature])
        
        # Handle numerical features
        numerical_features = data.select_dtypes(include=[np.number]).columns
        if "scaler" not in self.feature_preprocessors:
            self.feature_preprocessors["scaler"] = StandardScaler()
            processed_data[numerical_features] = self.feature_preprocessors["scaler"].fit_transform(data[numerical_features])
        else:
            processed_data[numerical_features] = self.feature_preprocessors["scaler"].transform(data[numerical_features])
        
        # Handle diagnosis codes
        if "diagnosis_codes" in data.columns:
            processed_data["diagnosis_count"] = data["diagnosis_codes"].apply(len)
            # TODO: Implement diagnosis code embedding
        
        return processed_data[self.features]
    
    def train(
        self,
        data: pd.DataFrame,
        target: str,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Train the readmission risk model."""
        try:
            # Preprocess features
            X = self.preprocess_features(data)
            y = data[target]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Initialize and train model
            self.model = xgb.XGBClassifier(**self.hyperparameters)
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            # Calculate metrics
            train_pred = self.model.predict_proba(X_train)[:, 1]
            test_pred = self.model.predict_proba(X_test)[:, 1]
            
            return {
                "status": "success",
                "metrics": {
                    "train_auc": self._calculate_auc(y_train, train_pred),
                    "test_auc": self._calculate_auc(y_test, test_pred),
                    "feature_importance": dict(zip(self.features, self.model.feature_importances_))
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate readmission risk predictions."""
        try:
            if self.model is None:
                raise ValueError("Model not trained")
            
            # Preprocess features
            X = self.preprocess_features(data)
            
            # Generate predictions
            risk_scores = self.model.predict_proba(X)[:, 1]
            
            return {
                "status": "success",
                "predictions": {
                    "risk_scores": risk_scores.tolist(),
                    "high_risk_threshold": 0.7,
                    "high_risk_patients": (risk_scores >= 0.7).sum()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_auc(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Area Under the ROC Curve."""
        from sklearn.metrics import roc_auc_score
        return roc_auc_score(y_true, y_pred)

class LengthOfStayModel:
    """Predicts patient length of stay."""
    
    def __init__(
        self,
        features: List[str],
        hyperparameters: Optional[Dict[str, Any]] = None
    ):
        self.features = features
        self.hyperparameters = hyperparameters or {
            "num_leaves": 31,
            "learning_rate": 0.05,
            "n_estimators": 150
        }
        self.model = None
        self.feature_preprocessors = {}
    
    def preprocess_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess features for model input."""
        processed_data = data.copy()
        
        # Handle categorical features
        categorical_features = data.select_dtypes(include=['object']).columns
        for feature in categorical_features:
            if feature not in self.feature_preprocessors:
                self.feature_preprocessors[feature] = LabelEncoder()
            processed_data[feature] = self.feature_preprocessors[feature].fit_transform(data[feature])
        
        # Handle numerical features
        numerical_features = data.select_dtypes(include=[np.number]).columns
        if "scaler" not in self.feature_preprocessors:
            self.feature_preprocessors["scaler"] = StandardScaler()
            processed_data[numerical_features] = self.feature_preprocessors["scaler"].fit_transform(data[numerical_features])
        else:
            processed_data[numerical_features] = self.feature_preprocessors["scaler"].transform(data[numerical_features])
        
        return processed_data[self.features]
    
    def train(
        self,
        data: pd.DataFrame,
        target: str,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Train the length of stay prediction model."""
        try:
            # Preprocess features
            X = self.preprocess_features(data)
            y = data[target]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Initialize and train model
            self.model = lgb.LGBMRegressor(**self.hyperparameters)
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            # Calculate metrics
            train_pred = self.model.predict(X_train)
            test_pred = self.model.predict(X_test)
            
            return {
                "status": "success",
                "metrics": {
                    "train_rmse": self._calculate_rmse(y_train, train_pred),
                    "test_rmse": self._calculate_rmse(y_test, test_pred),
                    "train_mae": self._calculate_mae(y_train, train_pred),
                    "test_mae": self._calculate_mae(y_test, test_pred),
                    "feature_importance": dict(zip(self.features, self.model.feature_importances_))
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate length of stay predictions."""
        try:
            if self.model is None:
                raise ValueError("Model not trained")
            
            # Preprocess features
            X = self.preprocess_features(data)
            
            # Generate predictions
            predictions = self.model.predict(X)
            
            return {
                "status": "success",
                "predictions": {
                    "los_predictions": predictions.tolist(),
                    "average_los": predictions.mean(),
                    "los_distribution": {
                        "min": predictions.min(),
                        "max": predictions.max(),
                        "median": np.median(predictions),
                        "std": predictions.std()
                    }
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Root Mean Squared Error."""
        return np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    def _calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Error."""
        return np.mean(np.abs(y_true - y_pred)) 