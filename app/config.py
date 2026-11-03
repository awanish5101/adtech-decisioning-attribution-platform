"""
Configuration settings for the AdTech Decisioning and Attribution Platform.
"""
import os
from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "AdTech Decisioning & Attribution Platform")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.5.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Real-Time Decisioning SLA Thresholds
    DECISION_TIMEOUT_MS: float = float(os.getenv("DECISION_TIMEOUT_MS", "15.0"))
    DEFAULT_FREQUENCY_CAP_PER_HOUR: int = int(os.getenv("DEFAULT_FREQUENCY_CAP_PER_HOUR", "3"))
    
    # Pacing and Minimum Bid Floors
    MIN_BID_CPM: float = float(os.getenv("MIN_BID_CPM", "0.10"))
    AUCTION_TYPE: str = os.getenv("AUCTION_TYPE", "FIRST_PRICE")
    
    # Storage & Observability
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
