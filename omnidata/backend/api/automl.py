from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from omnidata.scientist.automl import AutoML
from omnidata.utils.logging import get_logger
import json

logger = get_logger(__name__)
router = APIRouter(prefix="/api/automl", tags=["automl"])

# Initialize AutoML instance
automl = AutoML(
    auto_optimize=True,
    optimization_time=3600,
    max_memory_gb=8
)

class ModelConfig(BaseModel):
    targetColumn: str
    taskType: str
    autoOptimize: bool = True
    optimizationTime: int = 3600

class PredictionInput(BaseModel):
    data: Dict[str, Any]

@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        elif file.filename.endswith('.parquet'):
            df = pd.read_parquet(pd.io.common.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Generate data profile
        profile = automl._generate_data_profile(df)
        
        # Store the DataFrame for later use
        automl.data = df
        
        return {
            "message": "Data uploaded successfully",
            "profile": profile
        }
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_model(config: ModelConfig):
    try:
        if automl.data is None:
            raise HTTPException(status_code=400, detail="No data uploaded")

        # Configure AutoML instance
        automl.auto_optimize = config.autoOptimize
        automl.optimization_time = config.optimizationTime
        
        # Train model
        X = automl.data.drop(columns=[config.targetColumn])
        y = automl.data[config.targetColumn]
        
        model_results = automl.train_model(
            X=X,
            y=y,
            task_type=config.taskType
        )
        
        # Format results for frontend
        return {
            "model_info": {
                "type": model_results["model_type"],
                "parameters": model_results["parameters"]
            },
            "metrics": model_results["metrics"],
            "feature_importance": model_results["feature_importance"]
        }
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict(input_data: PredictionInput):
    try:
        if automl.model is None:
            raise HTTPException(status_code=400, detail="No model trained")

        # Convert input data to DataFrame
        input_df = pd.DataFrame([input_data.data])
        
        # Make predictions
        predictions = automl.predict(input_df)
        
        # Format predictions
        if isinstance(predictions, np.ndarray):
            predictions = predictions.tolist()
        
        return {
            "predictions": predictions,
            "probabilities": automl.predict_proba(input_df).tolist() if hasattr(automl, 'predict_proba') else None
        }
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    try:
        if automl.model is None:
            raise HTTPException(status_code=400, detail="No model trained")
            
        return {
            "model_type": automl.model_type,
            "feature_names": automl.feature_names,
            "target_name": automl.target_name,
            "metrics": automl.metrics,
            "parameters": automl.parameters
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 