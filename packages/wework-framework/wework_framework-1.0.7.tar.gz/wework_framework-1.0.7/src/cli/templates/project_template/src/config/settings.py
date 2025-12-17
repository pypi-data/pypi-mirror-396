"""Centralized settings configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    """Centralized settings class that loads environment variables."""
    
    def __init__(self):
        # Load environment variables from .env file
        project_root = Path(__file__).parent.parent.parent.resolve()
        env_path = project_root / '.env'
        load_dotenv(env_path)
        
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO').upper()

        # Database settings
        self.postgres_host: str = os.getenv('POSTGRES_HOST', 'localhost')
        self.postgres_user: str = os.getenv('POSTGRES_USER', 'postgres')
        self.postgres_password: str = os.getenv('POSTGRES_PASSWORD', '')
        self.postgres_db: str = os.getenv('POSTGRES_DB', '{{PROJECT_NAME_SNAKE}}')
        self.database_url: str = os.getenv(
            'DATABASE_URL', 
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:5432/{self.postgres_db}'
        )
        
        # JWT / Auth settings
        self.jwt_secret_key: str = os.getenv('JWT_SECRET_KEY', 'CHANGE_ME_SUPER_SECRET')
        self.jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
        self.jwt_access_token_expire_minutes: int = int(
            os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '60')
        )
        
        # Redis settings
        self.redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Frontend settings
        frontend_base = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173').strip()
        self.frontend_base_url: str = (frontend_base or 'http://localhost:5173').rstrip('/')


# Global settings instance
settings = Settings()

