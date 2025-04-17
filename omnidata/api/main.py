"""
OmniData.AI FastAPI Backend
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import json

from omnidata.stanleyai.agent import StanleyAI

# Initialize FastAPI app
app = FastAPI(
    title="OmniData.AI API",
    description="Enterprise-grade AI Data Platform API",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize StanleyAI
stanley = StanleyAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("LLM_MODEL", "gpt-4")
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class ETLRequest(BaseModel):
    source: str
    destination: str
    transform_steps: List[Dict[str, Any]]

class MLTrainRequest(BaseModel):
    dataset_path: str
    target_column: str
    model_type: str
    hyperparameters: Optional[Dict[str, Any]] = None

class DashboardRequest(BaseModel):
    data_source: str
    metrics: List[str]
    dimensions: List[str]
    filters: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "OmniData.AI API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.post("/stanley/ask")
async def ask_stanley(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Process a natural language query through StanleyAI."""
    try:
        response = await stanley.process_request(
            query=request.query,
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/etl/start")
async def start_etl_pipeline(
    request: ETLRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Start an ETL pipeline."""
    try:
        response = await stanley._handle_etl_tasks({
            "type": "etl",
            "source": request.source,
            "destination": request.destination,
            "transform_steps": request.transform_steps
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/train")
async def train_model(
    request: MLTrainRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Train a machine learning model."""
    try:
        response = await stanley._handle_ml_tasks({
            "type": "train",
            "dataset_path": request.dataset_path,
            "target_column": request.target_column,
            "model_type": request.model_type,
            "hyperparameters": request.hyperparameters
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bi/dashboard")
async def create_dashboard(
    request: DashboardRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Create a business intelligence dashboard."""
    try:
        response = await stanley._handle_bi_tasks({
            "type": "dashboard",
            "data_source": request.data_source,
            "metrics": request.metrics,
            "dimensions": request.dimensions,
            "filters": request.filters
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "stanley": "operational",
            "database": "operational",
            "ml_service": "operational"
        }
    } 