"""
AeroSight Backend Configuration Settings
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AeroSight API"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    api_prefix: str = "/api"
    
    # Database
    database_type: str = "duckdb"
    duckdb_path: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "warehouse.duckdb")
    
    # ML Models
    models_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "models")
    
    # Reports
    reports_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "output")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
