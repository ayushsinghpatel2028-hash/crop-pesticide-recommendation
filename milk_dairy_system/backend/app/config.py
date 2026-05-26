import os

class Settings:
    PROJECT_NAME: str = "Milk Dairy Management System"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    
    # JWT Auth Security (using static fallback, can be overridden by environment variables)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours - convenient for mobile use
    
    # Default admin credentials
    DEFAULT_ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

settings = Settings()
