from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/scroll-chat")
async def scroll_chat(req: ChatRequest):
    # Placeholder: Replace with ScrollPulse/OmniMind logic
    return {"reply": f"Scroll Scribe received: {req.message}"} 