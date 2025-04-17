from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path
import json
import uuid
import os

from omnidata.scientist.automl import AutoML

router = APIRouter(prefix="/api/automl", tags=["automl"])

# Store AutoML instances in memory (in production, use proper storage)
models = {}
datasets = {}

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
) -> Dict[str, Any]:
    """Upload a dataset for AutoML processing."""
    try:
        # Generate unique ID for the dataset
        dataset_id = str(uuid.uuid4())
        
        # Read the file based on extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension == '.csv':
            df = pd.read_csv(file.file)
        elif file_extension == '.parquet':
            df = pd.read_parquet(file.file)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_extension}. Please upload CSV or Parquet files."
            )
        
        # Generate data profile
        profile = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_stats": {},
            "categorical_stats": {}
        }
        
        # Profile numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            profile["numeric_stats"][col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "quartiles": df[col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        
        # Profile categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            profile["categorical_stats"][col] = {
                "unique_values": df[col].nunique(),
                "top_values": df[col].value_counts().head(10).to_dict()
            }
        
        # Store dataset
        datasets[dataset_id] = df
        
        return {
            "dataset_id": dataset_id,
            "profile": profile,
            "message": "Dataset uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_model(
    dataset_id: str,
    target_column: str,
    task_type: str = "classification",
    auto_optimize: bool = True,
    optimization_time: int = 3600,
) -> Dict[str, Any]:
    """Train an AutoML model on the uploaded dataset."""
    try:
        if dataset_id not in datasets:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset with ID {dataset_id} not found"
            )
        
        # Get dataset
        df = datasets[dataset_id]
        
        if target_column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Target column '{target_column}' not found in dataset"
            )
        
        # Initialize AutoML
        automl = AutoML(
            auto_optimize=auto_optimize,
            optimization_time=optimization_time
        )
        
        # Train model
        results = automl.train_model(
            df=df,
            target_column=target_column,
            task_type=task_type
        )
        
        # Generate model ID and store the model
        model_id = str(uuid.uuid4())
        models[model_id] = automl
        
        return {
            "model_id": model_id,
            "results": results,
            "message": "Model trained successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict(
    model_id: str,
    data: Dict[str, List[Any]],
    return_probabilities: bool = False
) -> Dict[str, Any]:
    """Make predictions using a trained model."""
    try:
        if model_id not in models:
            raise HTTPException(
                status_code=404,
                detail=f"Model with ID {model_id} not found"
            )
        
        # Get model
        automl = models[model_id]
        
        # Convert input data to DataFrame
        df = pd.DataFrame(data)
        
        # Make predictions
        predictions = automl.predict(df)
        response = {"predictions": predictions.tolist()}
        
        # Get probabilities if requested and available
        if return_probabilities and automl.task_type == "classification":
            probabilities = automl.predict_proba(df)
            if probabilities is not None:
                response["probabilities"] = probabilities.tolist()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/{model_id}")
async def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get information about a trained model."""
    try:
        if model_id not in models:
            raise HTTPException(
                status_code=404,
                detail=f"Model with ID {model_id} not found"
            )
        
        # Get model
        automl = models[model_id]
        
        return {
            "model_id": model_id,
            "task_type": automl.task_type,
            "feature_names": automl.feature_names,
            "auto_optimize": automl.auto_optimize,
            "optimization_time": automl.optimization_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List all trained models."""
    try:
        model_info = []
        for model_id, automl in models.items():
            model_info.append({
                "model_id": model_id,
                "task_type": automl.task_type,
                "feature_names": automl.feature_names,
                "auto_optimize": automl.auto_optimize,
                "optimization_time": automl.optimization_time
            })
        
        return {
            "models": model_info,
            "total_models": len(model_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 