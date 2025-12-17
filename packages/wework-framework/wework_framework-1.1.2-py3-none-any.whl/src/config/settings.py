"""Centralized settings configuration for the Wewework application."""
import os
from pathlib import Path
from typing import Optional
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
        self.postgres_db: str = os.getenv('POSTGRES_DB', 'wework')
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
        
        # Zarinpal settings
        # See: https://docs.zarinpal.com/paymentGateway/guide/
        self.zarinpal_merchant_id: str = os.getenv('ZARINPAL_MERCHANT_ID', '')
        # sandbox or www
        self.zarinpal_sandbox: bool = (
            os.getenv('ZARINPAL_SANDBOX', 'true').lower() == 'true'
        )
        self.zarinpal_callback_url: str = os.getenv(
            'ZARINPAL_CALLBACK_URL',
            'http://localhost:8000/api/billing/zarinpal/callback',
        )

        # Frontend redirect settings
        frontend_base = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173').strip()
        self.frontend_base_url: str = (frontend_base or 'http://localhost:5173').rstrip('/')

        success_path = os.getenv('PAYMENT_SUCCESS_PATH', '/payment/success') or '/payment/success'
        failure_path = os.getenv('PAYMENT_FAILURE_PATH', '/payment/failure') or '/payment/failure'
        if not success_path.startswith('/'):
            success_path = f'/{success_path}'
        if not failure_path.startswith('/'):
            failure_path = f'/{failure_path}'
        self.payment_success_path: str = success_path
        self.payment_failure_path: str = failure_path

        # WECAN SMS settings
        self.wecan_rest_url: Optional[str] = os.getenv('WECAN_REST_URL')
        self.wecan_token: Optional[str] = os.getenv('WECAN_TOKEN')
        self.wecan_from_number: Optional[str] = os.getenv('WECAN_FROM_NUMBER')
        self.wecan_otp_template_id: Optional[int] = os.getenv('WECAN_OTP_TEMPLATE_ID')
        
        # Web Push (VAPID) settings
        self.vapid_public_key: str = os.getenv('VAPID_PUBLIC_KEY', '')
        self.vapid_private_key: str = os.getenv('VAPID_PRIVATE_KEY', '')
        self.vapid_subject: str = os.getenv('VAPID_SUBJECT', 'mailto:admin@example.com')
    
    def get(self, key: str, default=None):
        """Get a specific setting by key, with optional default value."""
        return getattr(self, key, default)


# Global settings instance
settings = Settings()
