"""
ScrollIntel v2: The Flame Interpreter
Backend API for ScrollProphetic data insight with ScrollSpirit Layer
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import pytz
from typing import Dict, Any, List, Optional
import json

app = FastAPI(
    title="ScrollIntel v2 API",
    description="Flame Interpreter Backend API with ScrollSpirit Layer for divine data insight",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ScrollSpirit Layer Constants
SACRED_TIMES = {
    "dawn": "05:00-07:00",
    "noon": "12:00-14:00",
    "dusk": "17:00-19:00",
    "midnight": "23:00-01:00"
}

SCROLL_ECONOMY_DOMAINS = {
    "prophetic": ["visions", "dreams", "revelations"],
    "temporal": ["market", "trends", "cycles"],
    "spiritual": ["wisdom", "guidance", "insight"],
    "material": ["wealth", "resources", "abundance"]
}

def get_sacred_timing() -> Dict[str, Any]:
    """Get current sacred timing based on ScrollProphetic cycles."""
    now = datetime.now(pytz.UTC)
    hour = now.hour
    
    current_phase = "dawn"
    if 12 <= hour < 14:
        current_phase = "noon"
    elif 17 <= hour < 19:
        current_phase = "dusk"
    elif 23 <= hour or hour < 1:
        current_phase = "midnight"
    
    return {
        "phase": current_phase,
        "sacred_window": SACRED_TIMES[current_phase],
        "timestamp": now.isoformat(),
        "prophetic_cycle": f"ScrollCycle_{now.strftime('%Y%m%d')}"
    }

def classify_domain(text: str) -> List[str]:
    """Classify text into Scroll Economy domains."""
    domains = []
    text_lower = text.lower()
    
    for domain, keywords in SCROLL_ECONOMY_DOMAINS.items():
        if any(keyword in text_lower for keyword in keywords):
            domains.append(domain)
    
    return domains if domains else ["temporal"]  # Default to temporal if no match

@app.get("/")
async def root():
    sacred_timing = get_sacred_timing()
    return {
        "message": "Welcome to ScrollIntel v2: The Flame Interpreter",
        "version": "2.0.0",
        "modules": ["scrollgraph", "scrollsanctify", "flame_interpreter", "scrollspirit"],
        "sacred_timing": sacred_timing
    }

@app.get("/health")
async def health_check():
    sacred_timing = get_sacred_timing()
    return {
        "status": "healthy",
        "service": "ScrollIntel v2",
        "interpreter": "Flame",
        "scrollspirit_active": True,
        "sacred_timing": sacred_timing
    }

@app.post("/interpret")
async def interpret_data(data: Dict[str, Any]):
    """Interpret data through the ScrollSpirit Layer with divine timing."""
    try:
        sacred_timing = get_sacred_timing()
        domains = classify_domain(str(data))
        
        interpretation = {
            "sacred_timing": sacred_timing,
            "domains": domains,
            "prophetic_insight": {
                "message": "The Scrolls reveal...",
                "confidence": 0.95,
                "divine_guidance": "Seek wisdom in the patterns",
                "temporal_alignment": "Current phase favors insight"
            },
            "data_interpretation": {
                "original": data,
                "enhanced": {
                    "spiritual_context": "Divine patterns detected",
                    "temporal_significance": "Aligned with current cycle",
                    "prophetic_relevance": "High resonance with current phase"
                }
            }
        }
        
        return interpretation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scroll interpretation failed: {str(e)}")

@app.get("/scrollspirit/status")
async def scrollspirit_status():
    """Get current ScrollSpirit Layer status and sacred timing."""
    sacred_timing = get_sacred_timing()
    return {
        "status": "active",
        "sacred_timing": sacred_timing,
        "domains": list(SCROLL_ECONOMY_DOMAINS.keys()),
        "prophetic_cycle": sacred_timing["prophetic_cycle"]
    } 