from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    encoder_key: str
    database_url: str
    redis_caching_url: str
    redis_worker_url: str
    
    model_config = ConfigDict(env_file =".env")
    
settings = Settings()