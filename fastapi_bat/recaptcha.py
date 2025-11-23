from fastapi import APIRouter, Request, HTTPException
import httpx
from typing import Optional
import os
from config import settings

router = APIRouter()

@router.post("/recaptcha")
async def verify_recaptcha(request: Request):
    """
    Verify reCAPTCHA response similar to reCaptcha.php
    """
    try:
        # Get form data
        form_data = await request.form()
        recaptcha_response = form_data.get('g-recaptcha-response')
        
        if not recaptcha_response:
            raise HTTPException(status_code=400, detail="CPT001")  # No reCAPTCHA response provided
        
        if not settings.recaptcha_secret_key or settings.recaptcha_secret_key == '6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6':
            raise HTTPException(status_code=400, detail="CPT001")  # Secret key not configured
        
        # Verify with Google reCAPTCHA API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.recaptcha_secret_key,
                    'response': recaptcha_response,
                    'remoteip': request.client.host
                }
            )
            
            result = response.json()
            
            if result.get('success'):
                return {"status": "success", "message": "CPT000"}
            else:
                error_codes = result.get('error-codes', [])
                if 'invalid-input-secret' in error_codes:
                    return {"status": "error", "message": "CPT001"}  # Invalid secret
                elif 'invalid-input-response' in error_codes:
                    return {"status": "error", "message": "CPT002"}  # Invalid response
                else:
                    return {"status": "error", "message": "CPT002"}  # General error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CPT002: {str(e)}")

# Alternative endpoint that accepts JSON data
@router.post("/recaptcha/json")
async def verify_recaptcha_json(request: Request):
    """
    Verify reCAPTCHA response from JSON payload
    """
    try:
        json_data = await request.json()
        recaptcha_response = json_data.get('g-recaptcha-response') or json_data.get('recaptcha_response')
        
        if not recaptcha_response:
            raise HTTPException(status_code=400, detail="CPT001")  # No reCAPTCHA response provided
        
        if not settings.recaptcha_secret_key or settings.recaptcha_secret_key == '6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6':
            raise HTTPException(status_code=400, detail="CPT001")  # Secret key not configured
        
        # Verify with Google reCAPTCHA API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.recaptcha_secret_key,
                    'response': recaptcha_response,
                    'remoteip': request.client.host
                }
            )
            
            result = response.json()
            
            if result.get('success'):
                return {"status": "success", "message": "CPT000"}
            else:
                error_codes = result.get('error-codes', [])
                if 'invalid-input-secret' in error_codes:
                    return {"status": "error", "message": "CPT001"}
                elif 'invalid-input-response' in error_codes:
                    return {"status": "error", "message": "CPT002"}
                else:
                    return {"status": "error", "message": "CPT002"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CPT002: {str(e)}")

@router.get("/recaptcha/config")
async def get_recaptcha_config():
    """
    Get reCAPTCHA site key for frontend
    """
    return {
        "site_key": settings.recaptcha_site_key,
        "configured": settings.recaptcha_site_key != '6LcB0RUsAAAAANmYJjeuJOrzRm62JzFiaHjINw-g'
    }