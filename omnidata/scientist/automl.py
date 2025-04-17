"""
Enhanced AutoML module with advanced automation capabilities.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
import optuna
import mlflow
import joblib
from datetime import datetime
import logging
from pathlib import Path
import json
import os
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_selection import SelectKBest, mutual_info_classif, mutual_info_regression

class AutoML:
    """AutoML class for automated machine learning tasks."""

    def __init__(
        self,
        auto_optimize: bool = True,
        optimization_time: int = 3600,
        max_memory_gb: float = 4.0,
        random_state: int = 42,
    ):
        """Initialize AutoML with configuration parameters."""
        self.auto_optimize = auto_optimize
        self.optimization_time = optimization_time
        self.max_memory_gb = max_memory_gb
        self.random_state = random_state
        
        # Initialize components
        self.preprocessors = {}
        self.model = None
        self.feature_names = None
        self.target_encoder = None
        self.task_type = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _validate_data(self, df: pd.DataFrame, target_column: str) -> None:
        """Validate input data and target column."""
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")
        
        if df.empty:
            raise ValueError("DataFrame is empty")

    def _prepare_features(
        self,
        df: pd.DataFrame,
        target_column: str,
        is_training: bool = True,
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Prepare features for training or prediction."""
        # Split features and target
        X = df.drop(columns=[target_column])
        y = df[target_column] if is_training else None
        
        if is_training:
            self.feature_names = X.columns.tolist()
            
            # Initialize preprocessors for each column type
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            categorical_cols = X.select_dtypes(include=["object", "category"]).columns
            
            # Numeric preprocessing
            if len(numeric_cols) > 0:
                self.preprocessors["numeric"] = {
                    "imputer": SimpleImputer(strategy="mean"),
                    "scaler": StandardScaler(),
                    "columns": numeric_cols,
                }
                
                # Fit and transform numeric columns
                X_num = X[numeric_cols].values
                X_num = self.preprocessors["numeric"]["imputer"].fit_transform(X_num)
                X_num = self.preprocessors["numeric"]["scaler"].fit_transform(X_num)
                X[numeric_cols] = X_num
            
            # Categorical preprocessing
            if len(categorical_cols) > 0:
                self.preprocessors["categorical"] = {
                    "imputer": SimpleImputer(strategy="constant", fill_value="missing"),
                    "encoders": {},
                    "columns": categorical_cols,
                }
                
                # Fit and transform categorical columns
                for col in categorical_cols:
                    X[col] = self.preprocessors["categorical"]["imputer"].fit_transform(
                        X[[col]]
                    )
                    encoder = LabelEncoder()
                    X[col] = encoder.fit_transform(X[col])
                    self.preprocessors["categorical"]["encoders"][col] = encoder
            
            # Target preprocessing for classification
            if self.task_type == "classification":
                self.target_encoder = LabelEncoder()
                y = self.target_encoder.fit_transform(y)
        
        else:
            # Apply preprocessing for prediction
            if "numeric" in self.preprocessors:
                numeric_cols = self.preprocessors["numeric"]["columns"]
                X_num = X[numeric_cols].values
                X_num = self.preprocessors["numeric"]["imputer"].transform(X_num)
                X_num = self.preprocessors["numeric"]["scaler"].transform(X_num)
                X[numeric_cols] = X_num
            
            if "categorical" in self.preprocessors:
                categorical_cols = self.preprocessors["categorical"]["columns"]
                for col in categorical_cols:
                    X[col] = self.preprocessors["categorical"]["imputer"].transform(
                        X[[col]]
                    )
                    encoder = self.preprocessors["categorical"]["encoders"][col]
                    X[col] = encoder.transform(X[col])
        
        return X.values, y

    def train_model(
        self,
        df: pd.DataFrame,
        target_column: str,
        task_type: str = "classification",
    ) -> Dict[str, Any]:
        """Train an AutoML model on the provided dataset."""
        self._validate_data(df, target_column)
        self.task_type = task_type.lower()
        
        # Prepare data
        X, y = self._prepare_features(df, target_column, is_training=True)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=self.random_state,
        )
        
        # Initialize model based on task type
        if self.task_type == "classification":
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=self.random_state,
            )
        elif self.task_type == "regression":
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=self.random_state,
            )
        else:
            raise ValueError(f"Unsupported task type: {self.task_type}")
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Calculate feature importance
        feature_importance = []
        for name, importance in zip(self.feature_names, self.model.feature_importances_):
            feature_importance.append({
                "feature": name,
                "importance": float(importance),
            })
        
        # Calculate task-specific metrics
        metrics = {
            "train_score": float(train_score),
            "test_score": float(test_score),
        }
        
        if self.task_type == "classification":
            y_pred = self.model.predict(X_test)
            metrics.update({
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, average="weighted")),
                "recall": float(recall_score(y_test, y_pred, average="weighted")),
                "f1": float(f1_score(y_test, y_pred, average="weighted")),
            })
        else:
            y_pred = self.model.predict(X_test)
            metrics.update({
                "mse": float(mean_squared_error(y_test, y_pred)),
                "mae": float(mean_absolute_error(y_test, y_pred)),
                "r2": float(r2_score(y_test, y_pred)),
            })
        
        return {
            "metrics": metrics,
            "feature_importance": feature_importance,
        }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        # Prepare features
        X, _ = self._prepare_features(df, target_column=None, is_training=False)
        
        # Make predictions
        predictions = self.model.predict(X)
        
        # Decode predictions for classification
        if self.task_type == "classification" and self.target_encoder is not None:
            predictions = self.target_encoder.inverse_transform(predictions)
        
        return predictions

    def predict_proba(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """Get prediction probabilities for classification tasks."""
        if self.task_type != "classification":
            return None
        
        if not hasattr(self.model, "predict_proba"):
            return None
        
        # Prepare features
        X, _ = self._prepare_features(df, target_column=None, is_training=False)
        
        # Get probabilities
        probabilities = self.model.predict_proba(X)
        
        return probabilities

    def save_model(self, path: str) -> None:
        """Save the model and preprocessors to disk."""
        if self.model is None:
            raise ValueError("No model to save")
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(self.model, path / "model.joblib")
        
        # Save preprocessors
        joblib.dump(self.preprocessors, path / "preprocessors.joblib")
        
        # Save metadata
        metadata = {
            "feature_names": self.feature_names,
            "task_type": self.task_type,
            "created_at": datetime.now().isoformat(),
        }
        
        if self.target_encoder is not None:
            joblib.dump(self.target_encoder, path / "target_encoder.joblib")
            metadata["has_target_encoder"] = True
        
        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f)

    @classmethod
    def load_model(cls, path: str) -> "AutoML":
        """Load a saved model and preprocessors."""
        path = Path(path)
        
        # Create instance
        instance = cls()
        
        # Load model
        instance.model = joblib.load(path / "model.joblib")
        
        # Load preprocessors
        instance.preprocessors = joblib.load(path / "preprocessors.joblib")
        
        # Load metadata
        with open(path / "metadata.json", "r") as f:
            metadata = json.load(f)
        
        instance.feature_names = metadata["feature_names"]
        instance.task_type = metadata["task_type"]
        
        # Load target encoder if it exists
        if metadata.get("has_target_encoder", False):
            instance.target_encoder = joblib.load(path / "target_encoder.joblib")
        
        return instance