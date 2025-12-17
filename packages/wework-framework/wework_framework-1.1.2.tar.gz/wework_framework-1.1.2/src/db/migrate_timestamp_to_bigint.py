"""
Migration script to change candles.timestamp from INTEGER to BIGINT
Run this script once to update existing database schema.
"""
import asyncio
from sqlalchemy import text
from src.db.base import engine
from src.utils.logging import get_logger

logger = get_logger('migration')

async def migrate_timestamp_to_bigint():
    """Change candles.timestamp column from INTEGER to BIGINT."""
    async with engine.begin() as conn:
        try:
            # Check current column type
            result = await conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'candles' AND column_name = 'timestamp'
            """))
            current_type = result.scalar()
            
            if current_type == 'bigint':
                logger.info("✅ Column 'timestamp' is already BIGINT. No migration needed.")
                return
            
            logger.info(f"Current type: {current_type}. Migrating to BIGINT...")
            
            # For PostgreSQL, we need to alter the column type
            # This will work if there's no data, or we can use USING clause
            await conn.execute(text("""
                ALTER TABLE candles 
                ALTER COLUMN timestamp TYPE BIGINT 
                USING timestamp::BIGINT
            """))
            
            logger.info("✅ Successfully migrated candles.timestamp to BIGINT")
            
        except Exception as e:
            logger.error(f"❌ Error during migration: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(migrate_timestamp_to_bigint())

