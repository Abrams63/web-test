import logging
from fastapi import APIRouter, Request, HTTPException
import httpx
from typing import Optional
import os
from config import settings

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/recaptcha")
async def verify_recaptcha(request: Request):
    """
    Verify reCAPTCHA response similar to reCaptcha.php
    """
    logger.info(f"reCAPTCHA verification request from {request.client.host}")
    try:
        # Get form data
        form_data = await request.form()
        recaptcha_response = form_data.get('g-recaptcha-response')
        
        if not recaptcha_response:
            logger.warning("No reCAPTCHA response provided")
            raise HTTPException(status_code=400, detail="CPT001")  # No reCAPTCHA response provided
        
        if not settings.recaptcha_secret_key or settings.recaptcha_secret_key == '6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6':
            logger.error("reCAPTCHA secret key not configured properly")
            raise HTTPException(status_code=400, detail="CPT001")  # Secret key not configured
        
        # Verify with Google reCAPTCHA API
        async with httpx.AsyncClient() as client:
            logger.info("Sending verification request to Google reCAPTCHA API")
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
                logger.info("reCAPTCHA verification successful")
                return {"status": "success", "message": "CPT000"}
            else:
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA verification failed with errors: {error_codes}")
                if 'invalid-input-secret' in error_codes:
                    return {"status": "error", "message": "CPT001"}  # Invalid secret
                elif 'invalid-input-response' in error_codes:
                    return {"status": "error", "message": "CPT002"}  # Invalid response
                else:
                    return {"status": "error", "message": "CPT002"}  # General error
    except Exception as e:
        logger.error(f"Error during reCAPTCHA verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CPT002: {str(e)}")

# Alternative endpoint that accepts JSON data
@router.post("/recaptcha/json")
async def verify_recaptcha_json(request: Request):
    """
    Verify reCAPTCHA response from JSON payload
    """
    logger.info(f"reCAPTCHA JSON verification request from {request.client.host}")
    try:
        json_data = await request.json()
        recaptcha_response = json_data.get('g-recaptcha-response') or json_data.get('recaptcha_response')
        
        if not recaptcha_response:
            logger.warning("No reCAPTCHA response provided in JSON")
            raise HTTPException(status_code=400, detail="CPT01")  # No reCAPTCHA response provided
        
        if not settings.recaptcha_secret_key or settings.recaptcha_secret_key == '6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6':
            logger.error("reCAPTCHA secret key not configured properly for JSON endpoint")
            raise HTTPException(status_code=400, detail="CPT001")  # Secret key not configured
        
        # Verify with Google reCAPTCHA API
        async with httpx.AsyncClient() as client:
            logger.info("Sending JSON verification request to Google reCAPTCHA API")
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
                logger.info("reCAPTCHA JSON verification successful")
                return {"status": "success", "message": "CPT000"}
            else:
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA JSON verification failed with errors: {error_codes}")
                if 'invalid-input-secret' in error_codes:
                    return {"status": "error", "message": "CPT001"}
                elif 'invalid-input-response' in error_codes:
                    return {"status": "error", "message": "CPT002"}
                else:
                    return {"status": "error", "message": "CPT002"}
    except Exception as e:
        logger.error(f"Error during reCAPTCHA JSON verification: {str(e)}")
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