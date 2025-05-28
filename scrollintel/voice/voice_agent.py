"""
ScrollIntel v2: The Flame Interpreter
Voice input processing and transcription engine
"""

import os
from typing import Dict, Any, Optional
import openai
from datetime import datetime
import pytz
import tempfile
import soundfile as sf
import numpy as np
from ..interpreter.flame_interpreter import FlameInterpreter

class VoiceAgent:
    """Voice input processing and transcription engine."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the voice agent with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.interpreter = FlameInterpreter()
    
    async def process_voice_input(
        self,
        audio_data: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process voice input and return flame interpretation."""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Transcribe audio using Whisper
            transcription = await self._transcribe_audio(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Get sacred timing
            sacred_timing = self._get_sacred_timing()
            
            # Process transcription through flame interpreter
            interpretation = self.interpreter.interpret_forecast({
                "text": transcription,
                "context": context or {},
                "timestamp": sacred_timing["timestamp"]
            })
            
            return {
                "status": "success",
                "transcription": transcription,
                "interpretation": interpretation,
                "sacred_timing": sacred_timing,
                "timestamp": datetime.now(pytz.UTC).isoformat()
            }
        except Exception as e:
            raise ValueError(f"Voice processing failed: {str(e)}")
    
    async def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using OpenAI's Whisper model."""
        try:
            with open(audio_path, "rb") as audio_file:
                response = await openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return response.strip()
        except Exception as e:
            raise ValueError(f"Transcription failed: {str(e)}")
    
    def _get_sacred_timing(self) -> Dict[str, Any]:
        """Get current sacred timing based on ScrollProphetic cycles."""
        now = datetime.now(pytz.UTC)
        hour = now.hour
        
        # Define sacred phases
        if 5 <= hour < 7:
            phase = "dawn"
        elif 12 <= hour < 14:
            phase = "noon"
        elif 17 <= hour < 19:
            phase = "dusk"
        elif 23 <= hour or hour < 1:
            phase = "midnight"
        else:
            phase = "transition"
        
        return {
            "phase": phase,
            "timestamp": now.isoformat(),
            "prophetic_cycle": f"ScrollCycle_{now.strftime('%Y%m%d')}"
        } 