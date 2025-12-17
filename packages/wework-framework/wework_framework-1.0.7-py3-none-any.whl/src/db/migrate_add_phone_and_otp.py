"""
Migration script to add phone_number column to users table
and create login_otps table for SMS-based authentication.
Run once after pulling the new auth changes.
"""
import asyncio
from sqlalchemy import text
from src.db.base import engine
from src.utils.logging import get_logger

logger = get_logger("migration")


async def migrate_add_phone_and_otp():
    async with engine.begin() as conn:
        # 1) Add phone_number column to users table
        logger.info("Ensuring users.phone_number column exists...")
        await conn.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS phone_number VARCHAR;
                """
            )
        )

        logger.info("Adding unique constraint/index on users.phone_number...")
        await conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'uq_users_phone_number'
                    ) THEN
                        CREATE UNIQUE INDEX uq_users_phone_number ON users (phone_number)
                        WHERE phone_number IS NOT NULL;
                    END IF;
                END$$;
                """
            )
        )

        # 2) Create login_otps table if it does not exist
        logger.info("Ensuring login_otps table exists...")
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS login_otps (
                    id SERIAL PRIMARY KEY,
                    phone_number VARCHAR NOT NULL,
                    code_hash VARCHAR NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL,
                    verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
                );
                """
            )
        )

        logger.info("Adding indexes to login_otps...")
        await conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'ix_login_otps_phone_number'
                    ) THEN
                        CREATE INDEX ix_login_otps_phone_number ON login_otps(phone_number);
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'ix_login_otps_user_id'
                    ) THEN
                        CREATE INDEX ix_login_otps_user_id ON login_otps(user_id);
                    END IF;
                END$$;
                """
            )
        )

        logger.info("✅ Migration completed: phone_number column and login_otps table in place.")


if __name__ == "__main__":
    asyncio.run(migrate_add_phone_and_otp())


