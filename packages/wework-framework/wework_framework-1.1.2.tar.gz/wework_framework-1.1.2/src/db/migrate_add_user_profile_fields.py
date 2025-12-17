"""
Migration script to add username, bio, and avatar fields to users table.
Run this script once to update existing database schema.
"""
import asyncio
from sqlalchemy import text
from src.db.base import engine
from src.utils.logging import get_logger

logger = get_logger('migration')


async def migrate_add_user_profile_fields():
    """Add username, bio, and avatar columns to users table."""
    async with engine.begin() as conn:
        try:
            logger.info("Adding username, bio, and avatar columns to users table...")
            
            # Add username column
            await conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS username VARCHAR;
            """))
            
            # Add unique index on username (only for non-null values)
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'uq_users_username'
                    ) THEN
                        CREATE UNIQUE INDEX uq_users_username ON users (username)
                        WHERE username IS NOT NULL;
                    END IF;
                END$$;
            """))
            
            # Add bio column
            await conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS bio TEXT;
            """))
            
            # Add avatar column
            await conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS avatar VARCHAR;
            """))
            
            logger.info("✅ Successfully added username, bio, and avatar columns to users table")
            
        except Exception as e:
            logger.error(f"❌ Error during migration: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate_add_user_profile_fields())

