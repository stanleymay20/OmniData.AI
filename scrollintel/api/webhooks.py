from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import httpx
from ..core.auth import get_current_user
from ..core.config import settings

router = APIRouter()

class WebhookConfig(BaseModel):
    url: str
    platform: str
    secret: Optional[str] = None

class WebhookMessage(BaseModel):
    content: str
    forecast: dict
    timestamp: str

async def send_to_webhook(webhook: WebhookConfig, message: WebhookMessage):
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                headers["X-Webhook-Secret"] = webhook.secret

            response = await client.post(
                webhook.url,
                json=message.dict(),
                headers=headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending to webhook {webhook.url}: {str(e)}")
            return False

@router.post("/webhook/add")
async def add_webhook(
    webhook: WebhookConfig,
    current_user = Depends(get_current_user)
):
    """Add a new webhook endpoint for scroll insights"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can add webhooks")
    
    # Store webhook in database
    # TODO: Implement webhook storage
    
    return {"status": "success", "message": "Webhook added successfully"}

@router.post("/webhook/broadcast")
async def broadcast_insight(
    message: WebhookMessage,
    current_user = Depends(get_current_user)
):
    """Broadcast a scroll insight to all configured webhooks"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can broadcast insights")
    
    # Get all webhooks from database
    # TODO: Implement webhook retrieval
    
    # For now, use example webhooks
    webhooks = [
        WebhookConfig(url=settings.SLACK_WEBHOOK_URL, platform="slack"),
        WebhookConfig(url=settings.DISCORD_WEBHOOK_URL, platform="discord"),
        WebhookConfig(url=settings.TELEGRAM_WEBHOOK_URL, platform="telegram"),
        WebhookConfig(url=settings.WHATSAPP_WEBHOOK_URL, platform="whatsapp")
    ]
    
    results = []
    for webhook in webhooks:
        success = await send_to_webhook(webhook, message)
        results.append({
            "platform": webhook.platform,
            "success": success
        })
    
    return {
        "status": "success",
        "results": results
    } 