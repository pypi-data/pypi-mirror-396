from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings
import os

# Configure connection pool for better concurrency
# pool_size: number of connections to maintain persistently
# max_overflow: additional connections that can be created on demand
# pool_timeout: seconds to wait before giving up on getting a connection
# pool_recycle: seconds after which a connection is recreated (prevents stale connections)
pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))

engine = create_async_engine(
    settings.database_url,
    future=True,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_timeout=pool_timeout,
    pool_recycle=pool_recycle,
    pool_pre_ping=True,  # Verify connections before using them
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
