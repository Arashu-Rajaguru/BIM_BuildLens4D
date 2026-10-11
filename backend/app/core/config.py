import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "BuildLens 4D API")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database URL: defaults to local SQLite for modest hardware / zero-friction setup
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./buildlens4d.db")
    
    # CORS origins
    RAW_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )

    @property
    def cors_origins(self) -> List[str]:
        origins = [orig.strip() for orig in self.RAW_ORIGINS.split(",") if orig.strip()]
        # Allow wildcard for local development convenience or local network access
        if "*" not in origins and self.ENVIRONMENT == "development":
            origins.append("http://*")
        return origins

settings = Settings()
