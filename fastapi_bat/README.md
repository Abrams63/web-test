# BAT API Server

FastAPI replacement for bat folder functionality

## Configuration

To configure the application, create a `.env` file in the `fastapi_bat` directory with the following variables:

```env
# SMTP Settings
SMTP_USE_TLS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_RECIPIENT_EMAIL=recipient@gmail.com

# reCAPTCHA Settings
RECAPTCHA_SITE_KEY=your_site_key
RECAPTCHA_SECRET_KEY=your_secret_key

# Caching Settings
CACHE_ENABLED=true
CACHE_LIFETIME=3600
CACHE_DIR=cache

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false

# Search Settings
SEARCH_DIR=..
SEARCH_EXTENSIONS=["html", "htm"]
```

## Running the Application

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## Testing the Application

The application provides the following endpoints for testing:

- `GET /` - Main endpoint that returns server status and available endpoints
- `POST /mailform` - Handle form submissions and send emails
- `GET /api/search` - Search functionality
- `POST /api/recaptcha` - Verify reCAPTCHA response
- `GET /api/recaptcha/config` - Get reCAPTCHA site key for frontend

## Endpoints

- `POST /mailform` - Handle form submissions and send emails
- `GET /api/search` - Search functionality
- `POST /api/recaptcha` - Verify reCAPTCHA response
- `GET /api/recaptcha/config` - Get reCAPTCHA site key for frontend

FastAPI replacement for the original `bat` folder functionality, providing email forms, search, and reCAPTCHA verification.

## Features

- Email form processing with SMTP support
- Site search functionality
- reCAPTCHA verification
- Configuration via .env file or JSON config

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone or copy the project files
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Using Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your configuration values:
   - SMTP settings for email delivery
   - reCAPTCHA keys for verification
   - Other optional settings

### Using JSON Config

Alternatively, create a `config.json` file in the root directory with the following structure:

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your_email@gmail.com",
  "smtp_password": "your_app_password",
  "smtp_recipient_email": "recipient@gmail.com",
  "recaptcha_site_key": "your_site_key",
  "recaptcha_secret_key": "your_secret_key",
  "cache_enabled": true,
  "cache_lifetime": 3600,
  "app_host": "0.0.0.0",
  "app_port": 8000,
  "debug": false
}
```

## Usage

Start the server:
```bash
uvicorn fastapi_bat.main:app --reload --host 0.0.0.0 --port 8000
```

Or run directly:
```bash
python -m fastapi_bat.main
```

## API Endpoints

- `POST /mailform` - Process email forms
- `GET /api/search` - Site search functionality
- `POST /api/recaptcha` - Verify reCAPTCHA responses
- `GET /api/recaptcha/config` - Get reCAPTCHA configuration

## Integration with Existing Site

To integrate with your existing HTML site:

1. Update form action URLs to point to your FastAPI server
2. Update JavaScript to use the new API endpoints
3. For search functionality, update the search form to call `/api/search`
4. For reCAPTCHA, ensure the verification calls go to `/api/recaptcha`

## Endpoints Details

### Mailform Endpoint
```javascript
POST /mailform
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hello world!",
  "phone": "+1234567890",
  "form_type": "contact",
  "g_recaptcha_response": "recaptcha_token_here",
  "additional_fields": {
    "subject": "Inquiry"
  }
}
```

### Search Endpoint
```javascript
GET /api/search?s=search+query&filter=*.html
```

### reCAPTCHA Endpoint
```javascript
POST /api/recaptcha
Content-Type: application/x-www-form-urlencoded

g-recaptcha-response=token_here
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SMTP_HOST | smtp.gmail.com | SMTP server host |
| SMTP_PORT | 587 | SMTP server port |
| SMTP_USERNAME | demo@gmail.com | SMTP username |
| SMTP_PASSWORD | demopassword | SMTP password |
| SMTP_RECIPIENT_EMAIL | demo@gmail.com | Email recipient |
| RECAPTCHA_SITE_KEY | 6LdiOxUsAAAAAAFbiKNanTIu_8zOYEy8PExgEkml | reCAPTCHA site key |
| RECAPTCHA_SECRET_KEY | 6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6 | reCAPTCHA secret key |
| CACHE_ENABLED | true | Enable caching |
| CACHE_LIFETIME | 3600 | Cache lifetime in seconds |
| APP_HOST | 0.0.0.0 | Application host |
| APP_PORT | 8000 | Application port |
| DEBUG | false | Enable debug mode |

## Deployment

For production deployment, consider:

1. Using a process manager like `supervisor` or `systemd`
2. Setting up a reverse proxy with nginx
3. Using a WSGI/ASGI server like gunicorn
4. Securing your environment variables

Example with gunicorn:
```bash
gunicorn fastapi_bat.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0:8000



6LdiOxUsAAAAAAFbiKNanTIu_8zOYEy8PExgEkml ключ сайта

6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6 секретный ключ