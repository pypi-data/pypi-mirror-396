#!/usr/bin/env python3
"""
Database initialization wrapper that waits for database and creates tables.
This script can be used as an entrypoint for Docker containers.
"""
import asyncio
import sys
import time
from pathlib import Path

# Add app root to path (parent of src directory)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.base import engine
from src.db.create_tables import main as create_tables_main
from sqlalchemy import text
from src.config.settings import settings


async def wait_for_database(max_attempts=30, delay=2):
    """Wait for database to be ready."""
    print("⏳ Waiting for database to be ready...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return True
        except Exception as e:
            print(f"Attempt {attempt}/{max_attempts} - Database not ready: {e} | {settings.database_url}")
            if attempt < max_attempts:
                time.sleep(delay)
    
    print("❌ Database connection timeout after {} attempts".format(max_attempts))
    return False


async def initialize_database():
    """Initialize database by creating tables."""
    print("🗄️ Creating database tables...")
    
    try:
        await create_tables_main()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False


async def main():
    """Main entry point for database initialization."""
    print("🚀 Starting application with database initialization...")
    
    # Wait for database
    if not await wait_for_database():
        sys.exit(1)
    
    # Initialize database
    if not await initialize_database():
        sys.exit(1)
    
    print("🎉 Database initialization complete!")
    
    # Execute the original command
    if len(sys.argv) > 1:
        print(f"▶️ Starting main application: {' '.join(sys.argv[1:])}")
        # Use exec to replace the current process
        import os
        os.execvp(sys.argv[1], sys.argv[1:])
    else:
        print("▶️ No command provided")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())