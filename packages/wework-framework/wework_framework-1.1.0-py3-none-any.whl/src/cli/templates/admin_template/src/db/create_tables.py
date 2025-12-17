"""
Create database tables

Run with: python -m src.db.create_tables
"""
import asyncio
from sqlalchemy import text
from .base import engine, Base
from . import models


async def main():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(main())

