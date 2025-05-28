"""
ScrollIntel v2: The Flame Interpreter
FastAPI backend
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
import json
import logging
from pathlib import Path
import uuid

from ..interpreter.flame_interpreter import FlameInterpreter
from ..ui.scrollgraph import ScrollGraph
from ..sanctify.scrollsanctify import ScrollSanctify
from ..voice.voice_agent import VoiceAgent
from ..store.project_store import ProjectStore
from ..integrations.ga4_client import GA4Client
from ..integrations.dropbox_client import DropboxClient
from ..integrations.sheets_client import SheetsClient
from ..integrations.drive_client import DriveClient
from ..integrations.onedrive_client import OneDriveClient
from ..integrations.salesforce_client import SalesforceClient
from ..integrations.airtable_client import AirtableClient
from ..integrations.notion_client import NotionClient
from ..auth.jwt_auth import get_current_user, require_permission, TokenData
from ..auth.auth_service import auth_service, UserCreate
from ..assistants.scroll_prophet import scroll_prophet
from ..export.pdf_exporter import pdf_exporter
from ..integrations.github_client import github_client
from ..sync.cloud_sync import cloud_sync

# Initialize components
flame_interpreter = FlameInterpreter()
scroll_graph = ScrollGraph()
scroll_sanctify = ScrollSanctify()
voice_agent = VoiceAgent(os.getenv("OPENAI_API_KEY"))
project_store = ProjectStore()

# Initialize API
app = FastAPI(
    title="ScrollIntel v2 API",
    description="The Flame Interpreter API",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class InterpretRequest(BaseModel):
    data: Dict[str, Any]
    metrics: Optional[List[str]] = None

class VoicePromptRequest(BaseModel):
    audio_data: bytes
    sacred_timing: Optional[str] = None

class SanctifyRequest(BaseModel):
    data: Dict[str, Any]

class ResurrectRequest(BaseModel):
    session_id: Optional[str] = None
    domain: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: Optional[int] = 10

class GA4Request(BaseModel):
    property_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metrics: Optional[List[str]] = None
    dimensions: Optional[List[str]] = None

class DropboxRequest(BaseModel):
    path: Optional[str] = "/ScrollIntel"
    file_types: Optional[List[str]] = None

class SheetsRequest(BaseModel):
    sheet_url: str
    sheet_name: Optional[str] = None
    range_name: Optional[str] = None

class CloudStorageRequest(BaseModel):
    folder_id: Optional[str] = None
    file_types: Optional[List[str]] = None

class SalesforceRequest(BaseModel):
    """Salesforce request model."""
    object_name: str
    fields: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 1000

class AirtableRequest(BaseModel):
    """Airtable request model."""
    table_id: str
    fields: Optional[List[str]] = None
    filter_by_formula: Optional[str] = None
    max_records: Optional[int] = 100

class NotionRequest(BaseModel):
    """Notion request model."""
    database_id: str
    filter_by: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    page_size: Optional[int] = 100

# ScrollProphet request models
class InsightRequest(BaseModel):
    context: Dict[str, Any]

class RecommendationRequest(BaseModel):
    data: Dict[str, Any]

class GitHubExportRequest(BaseModel):
    """GitHub export request model."""
    repo_name: str
    commit_message: Optional[str] = None

# Dependency for GA4 client
async def get_ga4_client():
    client = GA4Client(
        credentials={
            "client_id": os.getenv("GA4_CLIENT_ID"),
            "client_secret": os.getenv("GA4_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GA4_REDIRECT_URI")
        }
    )
    return client

# Dependency for Dropbox client
async def get_dropbox_client():
    client = DropboxClient(
        credentials={
            "access_token": os.getenv("DROPBOX_ACCESS_TOKEN")
        }
    )
    return client

# Dependency for Sheets client
async def get_sheets_client():
    client = SheetsClient(
        credentials={
            "client_id": os.getenv("SHEETS_CLIENT_ID"),
            "client_secret": os.getenv("SHEETS_CLIENT_SECRET"),
            "redirect_uri": os.getenv("SHEETS_REDIRECT_URI")
        }
    )
    return client

# Dependency for Drive client
async def get_drive_client():
    client = DriveClient(
        credentials={
            "client_id": os.getenv("DRIVE_CLIENT_ID"),
            "client_secret": os.getenv("DRIVE_CLIENT_SECRET"),
            "redirect_uri": os.getenv("DRIVE_REDIRECT_URI")
        }
    )
    return client

# Dependency for OneDrive client
async def get_onedrive_client():
    client = OneDriveClient(
        credentials={
            "client_id": os.getenv("ONEDRIVE_CLIENT_ID"),
            "client_secret": os.getenv("ONEDRIVE_CLIENT_SECRET"),
            "tenant_id": os.getenv("ONEDRIVE_TENANT_ID")
        }
    )
    return client

def get_salesforce_client() -> SalesforceClient:
    """Get Salesforce client."""
    credentials = {
        "username": os.getenv("SALESFORCE_USERNAME"),
        "password": os.getenv("SALESFORCE_PASSWORD"),
        "security_token": os.getenv("SALESFORCE_SECURITY_TOKEN"),
        "domain": os.getenv("SALESFORCE_DOMAIN", "login")
    }
    return SalesforceClient(credentials)

def get_airtable_client() -> AirtableClient:
    """Get Airtable client."""
    credentials = {
        "api_key": os.getenv("AIRTABLE_API_KEY"),
        "base_id": os.getenv("AIRTABLE_BASE_ID")
    }
    return AirtableClient(credentials)

def get_notion_client() -> NotionClient:
    """Get Notion client."""
    credentials = {
        "api_key": os.getenv("NOTION_API_KEY")
    }
    return NotionClient(credentials)

# Authentication endpoints
@app.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service.update_last_login(user.username)
    access_token = auth_service.create_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register")
async def register(user_data: UserCreate):
    try:
        user = auth_service.create_user(user_data)
        access_token = auth_service.create_token(user.username)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/interpret")
async def interpret_data(request: InterpretRequest):
    """Interpret data and classify into Scroll Economy Domains."""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Interpret data
        interpretation = flame_interpreter.interpret_forecast(
            df,
            metrics=request.metrics
        )
        
        # Store session
        session_id = project_store.store_session(
            domain=interpretation["domain"],
            input_data=request.data,
            interpretation=interpretation,
            chart_path=None
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "interpretation": interpretation,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice")
async def process_voice(audio: UploadFile = File(...)):
    """Process voice input and return interpretation."""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Process voice input
        result = await voice_agent.process_voice_input(audio_data)
        
        # Store session
        session_id = project_store.store_session(
            domain=result["interpretation"]["domain"],
            input_data={"audio": "voice_input"},
            interpretation=result["interpretation"],
            chart_path=None,
            sacred_timing=result["sacred_timing"]
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "result": result,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resurrect")
async def resurrect_session(request: ResurrectRequest):
    """Retrieve past interpretation sessions."""
    try:
        if request.session_id:
            # Get specific session
            session = project_store.get_session(request.session_id)
            return {
                "status": "success",
                "session": session,
                "timestamp": datetime.now(pytz.UTC).isoformat()
            }
        else:
            # List sessions with filters
            sessions = project_store.list_sessions(
                domain=request.domain,
                start_date=request.start_date,
                end_date=request.end_date,
                limit=request.limit
            )
            return {
                "status": "success",
                "sessions": sessions,
                "timestamp": datetime.now(pytz.UTC).isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize")
async def create_visualization(request: InterpretRequest):
    """Create sacred visualization of data."""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Create visualization
        fig = scroll_graph.create_sacred_chart(
            data=df,
            chart_type="line",
            title="Sacred Visualization"
        )
        
        # Save chart
        chart_path = f"charts/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(chart_path)
        
        return {
            "status": "success",
            "chart_path": chart_path,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sanctify")
async def sanctify_data(request: SanctifyRequest):
    """Perform data sanctification checks."""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(request.data)
        
        # Sanctify data
        result = scroll_sanctify.sanctify_data(df)
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/ga4")
async def integrate_ga4(
    request: GA4Request,
    client: GA4Client = Depends(get_ga4_client)
):
    """Integrate with Google Analytics 4."""
    try:
        # Set default date range if not provided
        if not request.start_date:
            request.start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not request.end_date:
            request.end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Fetch metrics
        metrics = await client.fetch_data(
            property_id=request.property_id,
            date_range={
                "start_date": request.start_date,
                "end_date": request.end_date
            },
            metrics=request.metrics,
            dimensions=request.dimensions
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(metrics["metrics"])
        
        # Interpret metrics
        interpretation = flame_interpreter.interpret_forecast(
            df,
            metrics=request.metrics
        )
        
        # Create visualization
        fig = scroll_graph.create_sacred_chart(
            data=df,
            chart_type="line",
            title=f"GA4 Metrics: {interpretation['domain']}"
        )
        
        # Save chart
        chart_path = f"charts/ga4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(chart_path)
        
        # Store session
        session_id = project_store.store_session(
            domain=interpretation["domain"],
            input_data=metrics,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "ga4",
                "property_id": request.property_id,
                "date_range": {
                    "start": request.start_date,
                    "end": request.end_date
                }
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "metrics": metrics,
            "interpretation": interpretation,
            "chart_path": chart_path,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/dropbox")
async def integrate_dropbox(
    request: DropboxRequest,
    client: DropboxClient = Depends(get_dropbox_client)
):
    """Integrate with Dropbox."""
    try:
        # List files
        files = await client.list_resources(
            path=request.path,
            file_types=request.file_types
        )
        
        return {
            "status": "success",
            "files": files,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/dropbox/read")
async def read_dropbox_file(
    path: str,
    file_type: Optional[str] = None,
    client: DropboxClient = Depends(get_dropbox_client)
):
    """Read file from Dropbox and interpret."""
    try:
        # Read file
        data = await client.fetch_data(path, file_type)
        
        # Convert to DataFrame if needed
        df = client.to_dataframe(data)
        
        # Interpret data
        interpretation = flame_interpreter.interpret_forecast(df)
        
        # Create visualization
        fig = scroll_graph.create_sacred_chart(
            data=df,
            chart_type="line",
            title=f"Dropbox Data: {interpretation['domain']}"
        )
        
        # Save chart
        chart_path = f"charts/dropbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(chart_path)
        
        # Store session
        session_id = project_store.store_session(
            domain=interpretation["domain"],
            input_data=data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "dropbox",
                "path": path,
                "file_type": file_type
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data,
            "interpretation": interpretation,
            "chart_path": chart_path,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/sheets")
async def integrate_sheets(
    request: SheetsRequest,
    client: SheetsClient = Depends(get_sheets_client)
):
    """Integrate with Google Sheets."""
    try:
        # Fetch data
        df = await client.fetch_data(
            sheet_url=request.sheet_url,
            sheet_name=request.sheet_name,
            range_name=request.range_name
        )
        
        # Interpret data
        interpretation = flame_interpreter.interpret_forecast(df)
        
        # Create visualization
        fig = scroll_graph.create_sacred_chart(
            data=df,
            chart_type="line",
            title=f"Google Sheets: {interpretation['domain']}"
        )
        
        # Save chart
        chart_path = f"charts/sheets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(chart_path)
        
        # Store session
        session_id = project_store.store_session(
            domain=interpretation["domain"],
            input_data=df.to_dict(orient="records"),
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "sheets",
                "sheet_url": request.sheet_url,
                "sheet_name": request.sheet_name,
                "range": request.range_name
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": df.to_dict(orient="records"),
            "interpretation": interpretation,
            "chart_path": chart_path,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/drive")
async def integrate_drive(
    request: CloudStorageRequest,
    client: DriveClient = Depends(get_drive_client)
):
    """Integrate with Google Drive."""
    try:
        # List files
        files = await client.list_resources(
            folder_id=request.folder_id,
            file_types=request.file_types
        )
        
        return {
            "status": "success",
            "files": files,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/drive/read")
async def read_drive_file(
    file_id: str,
    file_type: Optional[str] = None,
    client: DriveClient = Depends(get_drive_client)
):
    """Read file from Google Drive and interpret."""
    try:
        # Read file
        data = await client.fetch_data(file_id, file_type)
        
        # Convert to DataFrame if needed
        df = client.to_dataframe(data)
        
        # Interpret data
        interpretation = flame_interpreter.interpret_forecast(df)
        
        # Create visualization
        fig = scroll_graph.create_sacred_chart(
            data=df,
            chart_type="line",
            title=f"Google Drive: {interpretation['domain']}"
        )
        
        # Save chart
        chart_path = f"charts/drive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(chart_path)
        
        # Store session
        session_id = project_store.store_session(
            domain=interpretation["domain"],
            input_data=data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "drive",
                "file_id": file_id,
                "file_type": file_type
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data,
            "interpretation": interpretation,
            "chart_path": chart_path,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/onedrive")
async def integrate_onedrive(
    request: CloudStorageRequest,
    client: OneDriveClient = Depends(get_onedrive_client)
):
    """Integrate with OneDrive."""
    try:
        # List files
        files = await client.list_resources(
            folder_id=request.folder_id,
            file_types=request.file_types
        )
        
        return {
            "status": "success",
            "files": files,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/onedrive/read")
async def read_onedrive_file(
    file_id: str,
    file_type: Optional[str] = None,
    client: OneDriveClient = Depends(get_onedrive_client)
):
    """Read file from OneDrive and interpret."""
    try:
        # Read file
        data = await client.fetch_data(file_id, file_type)
        
        # Convert to DataFrame if needed
        df = client.to_dataframe(data)
        
        # Interpret data
        interpretation = flame_interpreter.interpret_forecast(df)
        
        # Create visualization
        fig = scroll_graph.create_sacred_chart(
            data=df,
            chart_type="line",
            title=f"OneDrive: {interpretation['domain']}"
        )
        
        # Save chart
        chart_path = f"charts/onedrive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.write_image(chart_path)
        
        # Store session
        session_id = project_store.store_session(
            domain=interpretation["domain"],
            input_data=data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "onedrive",
                "file_id": file_id,
                "file_type": file_type
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": data.to_dict(orient="records") if isinstance(data, pd.DataFrame) else data,
            "interpretation": interpretation,
            "chart_path": chart_path,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/integrate/salesforce")
async def list_salesforce_objects(
    client: SalesforceClient = Depends(get_salesforce_client)
):
    """List available Salesforce objects."""
    try:
        objects = await client.list_resources()
        return {
            "status": "success",
            "objects": objects
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list Salesforce objects: {str(e)}"
        )

@app.get("/integrate/salesforce/{object_name}")
async def get_salesforce_object_info(
    object_name: str,
    client: SalesforceClient = Depends(get_salesforce_client)
):
    """Get information about a Salesforce object."""
    try:
        info = await client.get_resource_info(object_name)
        return {
            "status": "success",
            "info": info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get object info: {str(e)}"
        )

@app.post("/integrate/salesforce/read")
async def read_salesforce_data(
    request: SalesforceRequest,
    client: SalesforceClient = Depends(get_salesforce_client),
    interpreter: FlameInterpreter = Depends(flame_interpreter)
):
    """Read and interpret data from Salesforce."""
    try:
        # Fetch data from Salesforce
        df = await client.fetch_data(
            object_name=request.object_name,
            fields=request.fields,
            conditions=request.conditions,
            limit=request.limit
        )
        
        # Convert to dictionary for interpretation
        data = df.to_dict(orient="records")
        
        # Interpret data
        interpretation = await interpreter.interpret_data(data)
        
        # Create visualization
        graph = ScrollGraph()
        chart_path = graph.create_visualization(
            data,
            interpretation,
            f"salesforce_{request.object_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        # Store session
        session_id = str(uuid.uuid4())
        project_store.store_session(
            domain=interpretation["domain"],
            input_data=data,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "object_name": request.object_name,
                "fields": request.fields,
                "conditions": request.conditions,
                "limit": request.limit
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": data,
            "interpretation": interpretation,
            "chart_path": chart_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read Salesforce data: {str(e)}"
        )

@app.get("/integrate/airtable")
async def list_airtable_tables(
    client: AirtableClient = Depends(get_airtable_client)
):
    """List available Airtable tables."""
    try:
        tables = await client.list_resources()
        return {
            "status": "success",
            "tables": tables
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list Airtable tables: {str(e)}"
        )

@app.get("/integrate/airtable/{table_id}")
async def get_airtable_table_info(
    table_id: str,
    client: AirtableClient = Depends(get_airtable_client)
):
    """Get information about an Airtable table."""
    try:
        info = await client.get_resource_info(table_id)
        return {
            "status": "success",
            "info": info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get table info: {str(e)}"
        )

@app.post("/integrate/airtable/read")
async def read_airtable_data(
    request: AirtableRequest,
    client: AirtableClient = Depends(get_airtable_client),
    interpreter: FlameInterpreter = Depends(flame_interpreter)
):
    """Read and interpret data from Airtable."""
    try:
        # Fetch data from Airtable
        df = await client.fetch_data(
            table_id=request.table_id,
            fields=request.fields,
            filter_by_formula=request.filter_by_formula,
            max_records=request.max_records
        )
        
        # Convert to dictionary for interpretation
        data = df.to_dict(orient="records")
        
        # Interpret data
        interpretation = await interpreter.interpret_data(data)
        
        # Create visualization
        graph = ScrollGraph()
        chart_path = graph.create_visualization(
            data,
            interpretation,
            f"airtable_{request.table_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        # Store session
        session_id = str(uuid.uuid4())
        project_store.store_session(
            domain=interpretation["domain"],
            input_data=data,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "airtable",
                "table_id": request.table_id,
                "fields": request.fields,
                "filter_by_formula": request.filter_by_formula,
                "max_records": request.max_records
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": data,
            "interpretation": interpretation,
            "chart_path": chart_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read Airtable data: {str(e)}"
        )

@app.get("/integrate/notion")
async def list_notion_databases(
    client: NotionClient = Depends(get_notion_client)
):
    """List available Notion databases."""
    try:
        databases = await client.list_resources()
        return {
            "status": "success",
            "databases": databases
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list Notion databases: {str(e)}"
        )

@app.get("/integrate/notion/{database_id}")
async def get_notion_database_info(
    database_id: str,
    client: NotionClient = Depends(get_notion_client)
):
    """Get information about a Notion database."""
    try:
        info = await client.get_resource_info(database_id)
        return {
            "status": "success",
            "info": info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database info: {str(e)}"
        )

@app.post("/integrate/notion/read")
async def read_notion_data(
    request: NotionRequest,
    client: NotionClient = Depends(get_notion_client),
    interpreter: FlameInterpreter = Depends(flame_interpreter)
):
    """Read and interpret data from Notion."""
    try:
        # Fetch data from Notion
        df = await client.fetch_data(
            database_id=request.database_id,
            filter_by=request.filter_by,
            sorts=request.sorts,
            page_size=request.page_size
        )
        
        # Convert to dictionary for interpretation
        data = df.to_dict(orient="records")
        
        # Interpret data
        interpretation = await interpreter.interpret_data(data)
        
        # Create visualization
        graph = ScrollGraph()
        chart_path = graph.create_visualization(
            data,
            interpretation,
            f"notion_{request.database_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        # Store session
        session_id = str(uuid.uuid4())
        project_store.store_session(
            domain=interpretation["domain"],
            input_data=data,
            interpretation=interpretation,
            chart_path=chart_path,
            metadata={
                "source": "notion",
                "database_id": request.database_id,
                "filter_by": request.filter_by,
                "sorts": request.sorts,
                "page_size": request.page_size
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "data": data,
            "interpretation": interpretation,
            "chart_path": chart_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read Notion data: {str(e)}"
        )

@app.post("/export/tableau")
async def export_to_tableau(
    session_id: str,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Export session data to Tableau CSV format."""
    try:
        # Get session data
        session = project_store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Convert data to DataFrame
        df = pd.DataFrame(session["input_data"])
        
        # Add interpretation metadata
        df["scroll_domain"] = session["interpretation"]["domain"]
        df["flame_caption"] = session["interpretation"]["caption"]
        df["chart_path"] = session["chart_path"]
        df["timestamp"] = session["timestamp"]
        
        # Generate CSV filename
        filename = f"tableau_export_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join("exports", filename)
        
        # Create exports directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        return {
            "status": "success",
            "filepath": filepath,
            "filename": filename,
            "rows": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to Tableau: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(pytz.UTC).isoformat()
    }

@app.get("/integrations")
async def list_integrations(current_user: TokenData = Depends(require_permission("read"))):
    """List available integrations"""
    return {
        "integrations": [
            {"id": "drive", "name": "Google Drive", "type": "cloud_storage"},
            {"id": "onedrive", "name": "OneDrive", "type": "cloud_storage"},
            {"id": "airtable", "name": "Airtable", "type": "database"},
            {"id": "notion", "name": "Notion", "type": "database"},
            {"id": "salesforce", "name": "Salesforce", "type": "crm"}
        ]
    }

@app.get("/integrations/{integration_id}")
async def get_integration_info(
    integration_id: str,
    current_user: TokenData = Depends(require_permission("read"))
):
    """Get integration details"""
    # Implementation here
    pass

@app.post("/integrations/{integration_id}/connect")
async def connect_integration(
    integration_id: str,
    credentials: dict,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Connect to an integration"""
    # Implementation here
    pass

@app.post("/integrations/{integration_id}/disconnect")
async def disconnect_integration(
    integration_id: str,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Disconnect from an integration"""
    # Implementation here
    pass

@app.get("/datasets")
async def list_datasets(current_user: TokenData = Depends(require_permission("read"))):
    """List available datasets"""
    # Implementation here
    pass

@app.post("/interpret")
async def interpret_dataset(
    dataset_id: str,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Interpret a dataset"""
    # Implementation here
    pass

@app.get("/sessions")
async def list_sessions(current_user: TokenData = Depends(require_permission("read"))):
    """List user's sessions"""
    # Implementation here
    pass

@app.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: TokenData = Depends(require_permission("read"))
):
    """Get session details"""
    # Implementation here
    pass

@app.post("/export/tableau")
async def export_to_tableau(
    session_id: str,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Export session data to Tableau"""
    # Implementation here
    pass

# ScrollProphet endpoints
@app.post("/prophet/insights")
async def get_prophet_insights(
    request: InsightRequest,
    current_user: TokenData = Depends(require_permission("read"))
):
    """Get AI-powered insights from ScrollProphet."""
    try:
        insights = await scroll_prophet.get_insights(request.context)
        return {
            "status": "success",
            "insights": insights,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get insights: {str(e)}"
        )

@app.post("/prophet/recommendations")
async def get_prophet_recommendations(
    request: RecommendationRequest,
    current_user: TokenData = Depends(require_permission("read"))
):
    """Get AI-powered recommendations from ScrollProphet."""
    try:
        recommendations = await scroll_prophet.get_recommendations(request.data)
        return {
            "status": "success",
            "recommendations": recommendations,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@app.post("/export/pdf/{session_id}")
async def export_pdf(
    session_id: str,
    current_user: TokenData = Depends(require_permission("read"))
):
    """
    Export a session as a PDF report.
    """
    try:
        pdf_path = await pdf_exporter.generate_report(session_id)
        return {
            "status": "success",
            "message": "PDF report generated successfully",
            "file_path": pdf_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF report: {str(e)}"
        )

@app.post("/export/github/{session_id}")
async def export_to_github(
    session_id: str,
    request: GitHubExportRequest,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Export session data to GitHub repository."""
    try:
        # Get session data
        session = project_store.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Generate CSV content
        df = pd.DataFrame(session["input_data"])
        csv_content = df.to_csv(index=False)
        
        # Generate PDF content
        pdf_path = await pdf_exporter.generate_report(session_id)
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()
        
        # Prepare session data
        session_data = {
            "domain": session["domain"],
            "interpretation": session["interpretation"],
            "csv_content": csv_content,
            "pdf_content": pdf_content
        }
        
        # Push to GitHub
        commit_url = await github_client.push_session(
            repo_name=request.repo_name,
            session_data=session_data,
            commit_message=request.commit_message
        )
        
        # Update session with GitHub commit URL
        session["github_commit_url"] = commit_url
        project_store.update_session(session_id, session)
        
        return {
            "status": "success",
            "message": "Successfully pushed to GitHub",
            "commit_url": commit_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to GitHub: {str(e)}"
        )

@app.post("/sync/cloud")
async def trigger_cloud_sync(
    current_user: TokenData = Depends(require_permission("write"))
):
    """Trigger manual cloud sync."""
    try:
        result = await cloud_sync.sync_all_sources()
        return {
            "status": "success",
            "message": "Cloud sync completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync cloud sources: {str(e)}"
        )

@app.post("/sync/{source}")
async def trigger_source_sync(
    source: str,
    current_user: TokenData = Depends(require_permission("write"))
):
    """Trigger sync for a specific cloud source."""
    if source not in ["dropbox", "drive", "onedrive"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {source}"
        )
    
    try:
        result = await cloud_sync.sync_source(source)
        return {
            "status": "success",
            "message": f"{source.title()} sync completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync {source}: {str(e)}"
        )

@app.get("/sync/status")
async def get_sync_status(
    current_user: TokenData = Depends(require_permission("read"))
):
    """Get current cloud sync status."""
    try:
        status = cloud_sync.get_sync_status()
        return {
            "status": "success",
            "sync_status": status
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )

@app.get("/api/sync/status")
async def get_sync_status(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current sync status for all cloud sources"""
    return cloud_sync.get_sync_status()

@app.post("/api/sync/trigger")
async def trigger_sync(current_user: Dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Trigger manual sync of all cloud sources"""
    try:
        await cloud_sync.sync_all_sources()
        return {"status": "success", "message": "Sync triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/trigger/{source}")
async def trigger_source_sync(
    source: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Trigger manual sync for a specific cloud source"""
    if source not in ["dropbox", "gdrive", "onedrive"]:
        raise HTTPException(status_code=400, detail="Invalid source")
        
    try:
        if source == "dropbox":
            await cloud_sync.sync_dropbox()
        elif source == "gdrive":
            await cloud_sync.sync_gdrive()
        elif source == "onedrive":
            await cloud_sync.sync_onedrive()
            
        return {"status": "success", "message": f"{source} sync triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 