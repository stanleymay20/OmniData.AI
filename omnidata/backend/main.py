"""
ScrollIntel v2: The Flame Interpreter
Backend API for ScrollProphetic data insight
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="ScrollIntel v2 API",
    description="Flame Interpreter Backend API for ScrollProphetic data insight",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Welcome to ScrollIntel v2: The Flame Interpreter",
        "version": "2.0.0",
        "modules": ["scrollgraph", "scrollsanctify", "flame_interpreter"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ScrollIntel v2",
        "interpreter": "Flame"
    } 