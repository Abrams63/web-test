try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # SMTP Settings
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "demo@gmail.com"
    smtp_password: str = "demopassword"
    smtp_recipient_email: str = "demo@gmail.com"
    
    # reCAPTCHA Settings
    recaptcha_site_key: str = "6LcB0RUsAAAAANmYJjeuJOrzRm62JzFiaHjINw-g"
    recaptcha_secret_key: str = "6LdbyxUsAAAAAH7ugiBN4F9r1eQoK0YsCScApsN6"
        
    # Caching Settings
    cache_enabled: bool = True
    cache_lifetime: int = 3600  # in seconds
    cache_dir: str = "cache"
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Search Settings
    search_dir: str = ".."  # Relative to the web root
    search_extensions: list = ["html", "htm"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    
    @property
    def smtp_start_tls(self) -> bool:
        """Determine if STARTTLS should be used based on configuration"""
        # STARTTLS should not be used if SSL is already enabled
        return self.smtp_use_tls and not self.smtp_use_ssl and self.smtp_port in [587, 25]

# Create settings instance
settings = Settings()

# Create cache directory if it doesn't exist
Path(settings.cache_dir).mkdir(exist_ok=True)

# Export all settings as a dictionary
def get_settings_dict():
    return settings.dict()

# Function to load settings from JSON file as alternative to .env
def load_settings_from_json(json_path: str = "config.json"):
    import json
    from pathlib import Path
    
    config_path = Path(json_path)
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Update settings with values from JSON file
        for key, value in config_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
    
    return settings