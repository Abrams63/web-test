import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from pathlib import Path
import asyncio
from datetime import datetime
from config import settings
from search import router as search_router
from recaptcha import router as recaptcha_router

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="BAT API Server", description="FastAPI replacement for bat folder functionality")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router, prefix="/api", tags=["search"])
app.include_router(recaptcha_router, prefix="/api", tags=["recaptcha"])

# Pydantic models
class MailFormData(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    message: str
    phone: Optional[str] = None
    form_type: str # contact, subscribe, order
    g_recaptcha_response: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None

# Mail configuration model
class MailConfig(BaseModel):
    useSmtp: bool
    host: str
    port: int
    username: str
    password: str
    recipientEmail: str

# Load configuration
def load_config():
    # Using settings from config.py
    return MailConfig(
        useSmtp=True,
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        recipientEmail=settings.smtp_recipient_email
    )

# Email template
def create_email_template(data: MailFormData, config: MailConfig, hostname: str = "localhost") -> str:
    subject_map = {
        "contact": "A message from your site visitor",
        "subscribe": "Subscribe request",
        "order": "Order request"
    }
    
    subject = subject_map.get(data.form_type, "A message from your site visitor")
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{subject}</title>
    </head>
    <body style="background: #406c8d; font-family: Arial, sans-serif;">
        <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td align="center" valign="top" style="padding: 0 15px;background: #406c8d;">
                    <table align="center" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td height="15" style="height: 15px; line-height:15px;"></td>
                        </tr>
                        <tr>
                            <td width="600" align="center" valign="top" style="border-radius: 4px; overflow: hidden; box-shadow: 3px 3px 6px 0 rgba(0,0,0.2);background: #dde1e6;">
                                <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="center" valign="top" style="border-top-left-radius: 4px; border-top-right-radius: 4px; overflow: hidden; padding: 0 20px;background: #302f35;">
                                            <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                <tr>
                                                    <td height="30" style="height: 30px; line-height:30px;"></td>
                                                </tr>
                                                <tr>
                                                    <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 32px; mso-line-height-rule: exactly; line-height: 32px; font-weight: 400; letter-spacing: 1px;color: #ffffff;">Notification</td>
                                                </tr>
                                                <tr>
                                                    <td height="30" style="height: 30px; line-height:30px;"></td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" valign="top" style="padding: 0 20px;">
                                            <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                <tr>
                                                    <td height="30" style="height: 30px; line-height:30px;"></td>
                                                </tr> 
                                                <tr> 
                                                    <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 22px; font-weight: 400;color: #302f35;">Hi, someone left a message for you at {hostname}</td>
                                                </tr>
                                                <tr> 
                                                    <td height="20" style="height: 20px; line-height:20px;"></td>
                                                </tr>
                                                <tr>
                                                    <td align="center" valign="top">
                                                        <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                            <tr>
                                                                <td align="center" valign="top" style="background: #d1d5da;">
                                                                    <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                                        <tr>
                                                                            <td height="1" style="height: 1px; line-height:1px;"></td>
                                                                        </tr>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td align="center" valign="top" style="background: #e4e6e9;">
                                                                    <table width="10%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                                        <tr>
                                                                            <td height="2" style="height: 2px; line-height:2px;"></td>
                                                                        </tr>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td height="20" style="height: 20px; line-height:20px;"></td>
                                                </tr>
                                                <tr>
                                                    <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 24px; mso-line-height-rule: exactly; line-height: 30px; font-weight: 700;color: #302f35;">
                                                    	{subject}
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td height="20" style="height: 20px; line-height:20px;"></td>
                                                </tr>
                                                <tr>
                                                    <td align="center" valign="top">
                                                        <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                            <tr>
                                                                <td align="center" valign="top">
                                                                    <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                                                        <tr>
                                                                            <td width="110" align="left" valign="top" style="padding: 0 10px 0 0;font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">Email:</td>
                                                                            <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">{data.email}</td> 
                                                                        </tr>
                                                                        <tr>
                                                                            <td width="110" align="left" valign="top" style="padding: 0 10px 0 0;font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">Name:</td>
                                                                            <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">{data.name or 'Not provided'}</td>
                                                                        </tr>
                                                                        {f'<tr><td width="110" align="left" valign="top" style="padding: 0 10px 0 0;font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">Phone:</td><td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">{data.phone}</td></tr>' if data.phone else ''}
                                                                        {"".join([f'<tr><td width="110" align="left" valign="top" style="padding: 0 10px 0 0;font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">{k.capitalize()}:</td><td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">{v}</td></tr>' for k, v in (data.additional_fields or {}).items()])}
                                                                        <tr>
                                                                            <td height="12" style="height: 12px; line-height:12px;"></td>
                                                                        </tr>
                                                                        <tr>
                                                                            <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">Message:</td>
                                                                        </tr>
                                                                        <tr>
                                                                            <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">
                                                                            {data.message}
                                                                            </td>
                                                                        </tr>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td height="12" style="height: 12px; line-height:12px;"></td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td height="40" style="height: 40px; line-height:40px;"></td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td height="20" style="height: 20px; line-height:20px;"></td>
                        </tr>
                        <tr>
                            <td width="600" align="center" valign="top">
                                <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="center" valign="top" style="font-family: Arial, sans-serif; font-size: 12px; mso-line-height-rule: exactly; line-height: 18px; font-weight: 400;color: #a1b4c4;">This is an automatically generated email, please do not reply.</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td height="20" style="height: 20px; line-height:20px;"></td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_template

async def send_email_async(data: MailFormData, hostname: str = "localhost"):
    config = load_config()
    
    # Create message
    msg = MIMEMultipart("alternative")
    msg['Subject'] = (
        "A message from your site visitor" if data.form_type == "contact" 
        else "Subscribe request" if data.form_type == "subscribe" 
        else "Order request" if data.form_type == "order" 
        else "A message from your site visitor"
    )
    msg['From'] = config.username
    msg['To'] = config.recipientEmail
    
    # Create HTML content
    html_content = create_email_template(data, config, hostname)
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)
    
    if config.useSmtp:
        # Send via SMTP
        try:
            import logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            logger.info(f"Attempting to send email to: {config.recipientEmail}")
            logger.info(f"SMTP Host: {config.host}, Port: {config.port}")
            logger.info(f"Using SSL: {settings.smtp_use_ssl}, Using STARTTLS: {settings.smtp_start_tls}")
            
            if settings.smtp_use_ssl:
                logger.info("Creating SMTP connection with SSL")
                smtp = aiosmtplib.SMTP(hostname=config.host, port=config.port)
                await smtp.connect(use_tls=True, start_tls=False)
            else:
                logger.info("Creating SMTP connection with STARTTLS")
                smtp = aiosmtplib.SMTP(hostname=config.host, port=config.port)
                await smtp.connect(use_tls=settings.smtp_start_tls)
                
            logger.info("Logging in to SMTP server")
            await smtp.login(config.username, config.password)
            logger.info("Sending email message")
            await smtp.send_message(msg)
            logger.info("Email sent successfully")
            await smtp.quit()
        except Exception as e:
            print(f"Error sending email: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    else:
        # For local testing without SMTP
        print(f"Email would be sent to {config.recipientEmail}")
        print(f"Subject: {msg['Subject']}")
        print(f"Content: {html_content}")

# Endpoint to handle both form data and JSON data
@app.post("/mailform")
async def handle_mailform(request: Request, background_tasks: BackgroundTasks):
    """
    Handle form submissions sent as JSON or application/x-www-form-urlencoded and send emails
    """
    try:
        logger.info(f"Received form submission from {request.client.host}")
        content_type = request.headers.get("content-type", "")
        mail_data = None

        if "application/json" in content_type:
            # Handle JSON request
            json_body = await request.json()
            mail_data = MailFormData(**json_body)
        else:
            # Handle form data request
            form_data = await request.form()
            name = form_data.get("name")
            email = form_data.get("email")
            message = form_data.get("message")
            phone = form_data.get("phone")
            # The form type might be sent as "form-type" from the JavaScript
            form_type = form_data.get("form_type") or form_data.get("form-type", "contact")
            g_recaptcha_response = form_data.get("g-recaptcha-response") or form_data.get("g_recaptcha_response")
            additional_fields_str = form_data.get("additional_fields")
            
            # Parse additional fields if provided as JSON string
            additional_fields_dict = None
            if additional_fields_str:
                try:
                    additional_fields_dict = json.loads(additional_fields_str)
                except json.JSONDecodeError:
                    # If not valid JSON, treat as a simple string
                    additional_fields_dict = {"additional": additional_fields_str}
            
            mail_data = MailFormData(
                name=name,
                email=email,
                message=message,
                phone=phone,
                form_type=form_type,
                g_recaptcha_response=g_recaptcha_response,
                additional_fields=additional_fields_dict
            )
        
        logger.info(f"Processing form of type: {mail_data.form_type} from {mail_data.email}")
        
        # Add to background task to avoid blocking the response
        background_tasks.add_task(send_email_async, mail_data, request.url.hostname)
        logger.info("Email task added to background tasks")
        return {"status": "success", "message": "Form submitted successfully"}
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (HTML, CSS, JS, images, etc.) from the parent directory
app.mount("/", StaticFiles(directory="../", html=True), name="static")


@app.get("/api/")
async def api_root():
    return {"message": "BAT API Server is running", "endpoints": ["/mailform", "/search", "/recaptcha", "/twitter"]}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0", port=8000)