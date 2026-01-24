from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    access_encoder_key: str
    refresh_encoder_key: str
    database_url: str
    redis_caching_url: str
    redis_worker_url: str
    hostname: str
    
    # SMTP Config
    smtp_server: str
    smtp_port: str
    smtp_user: str
    smtp_password: str
    
    model_config = ConfigDict(env_file =".env")
    
settings = Settings()