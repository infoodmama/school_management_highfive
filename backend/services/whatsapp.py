"""WhatsApp Meta Graph API service."""
import logging
import httpx
from datetime import datetime
from typing import Optional, Dict
from db import db

logger = logging.getLogger(__name__)



BASE_WA_URL = "https://crm.abhiit.com/api/meta/v19.0"

async def get_wa_settings():
    settings = await db.settings.find_one({"type": "whatsapp"}, {"_id": 0})
    if not settings or not settings.get('phoneNumberId') or not settings.get('accessToken'):
        return None
    return settings

async def send_wa_template(mobile, template_name, components, settings=None):
    """Send WhatsApp template message"""
    try:
        if not settings:
            settings = await get_wa_settings()
        if not settings:
            return {"success": False, "message": "WhatsApp not configured"}
        url = f"{BASE_WA_URL}/{settings['phoneNumberId']}/messages"
        headers = {"Authorization": f"Bearer {settings['accessToken']}", "Content-Type": "application/json"}
        payload = {
            "to": mobile,
            "recipient_type": "individual",
            "type": "template",
            "template": {
                "language": {"policy": "deterministic", "code": "en"},
                "name": template_name,
                "components": components
            }
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(url, headers=headers, json=payload, timeout=30.0)
            logger.info(f"WhatsApp template '{template_name}' sent to {mobile}: {response.status_code}")
            return {"success": True, "data": response.json()}
    except Exception as e:
        logger.error(f"WhatsApp send failed: {str(e)}")
        return {"success": False, "message": str(e)}

async def send_fee_paid_message(mobile, invoice_url, amount, fee_name, student_name, settings=None):
    """Send fee paid success with invoice document"""
    components = [
        {"type": "header", "parameters": [{"type": "document", "document": {"link": invoice_url}}]},
        {"type": "body", "parameters": [
            {"type": "text", "text": str(amount)},
            {"type": "text", "text": fee_name},
            {"type": "text", "text": student_name}
        ]}
    ]
    return await send_wa_template(mobile, "fee_paid_bill", components, settings)

async def send_absent_message(mobile, student_name, class_name, date_str, settings=None):
    """Send absent notification"""
    components = [
        {"type": "body", "parameters": [
            {"type": "text", "text": student_name},
            {"type": "text", "text": class_name},
            {"type": "text", "text": date_str}
        ]}
    ]
    return await send_wa_template(mobile, "absent_hifg", components, settings)

async def send_event_message(mobile, event_name, event_date, settings=None):
    """Send event notification"""
    components = [
        {"type": "body", "parameters": [
            {"type": "text", "text": event_name},
            {"type": "text", "text": event_date}
        ]}
    ]
    return await send_wa_template(mobile, "holi", components, settings)

# Backward-compat wrapper
async def send_whatsapp_message(mobile, message, settings=None):
    """Fallback text message (kept for fee reminders etc)"""
    try:
        if not settings:
            settings = await get_wa_settings()
        if not settings:
            return {"success": False, "message": "WhatsApp not configured"}
        url = f"{BASE_WA_URL}/{settings['phoneNumberId']}/messages"
        headers = {"Authorization": f"Bearer {settings['accessToken']}", "Content-Type": "application/json"}
        payload = {"to": mobile, "recipient_type": "individual", "type": "text", "text": {"body": message}}
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(url, headers=headers, json=payload, timeout=30.0)
            return {"success": True, "data": response.json()}
    except Exception as e:
        logger.error(f"WhatsApp send failed: {str(e)}")
        return {"success": False, "message": str(e)}
