import asyncio
from sqlalchemy import text
from .base import engine, Base
from . import models


async def cleanup_orphaned_sequences(conn):
    """Remove orphaned sequences that don't have corresponding tables."""
    # Get all existing tables
    result = await conn.execute(text("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    """))
    existing_tables = {row[0] for row in result}
    
    # Get tables we're about to create from metadata
    tables_to_create = set(Base.metadata.tables.keys())
    
    # For each table we're about to create, check if its ID sequence exists
    # but the table doesn't exist (orphaned sequence scenario)
    for table_name in tables_to_create:
        if table_name not in existing_tables:
            # Check if the ID sequence exists for this table
            # PostgreSQL creates sequences as: tablename_columnname_seq
            # For SERIAL primary keys, it's typically: tablename_id_seq
            seq_name = f"{table_name}_id_seq"
            
            # Check if sequence exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.sequences 
                    WHERE sequence_schema = 'public' AND sequence_name = :seq_name
                )
            """), {"seq_name": seq_name})
            
            if result.scalar():
                try:
                    await conn.execute(text(f'DROP SEQUENCE IF EXISTS "{seq_name}" CASCADE'))
                    print(f"🧹 Cleaned up orphaned sequence: {seq_name}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not drop sequence {seq_name}: {e}")


async def main():
    async with engine.begin() as conn:
        # Clean up orphaned sequences before creating tables
        await cleanup_orphaned_sequences(conn)
        # Create all tables (checkfirst=True ensures we don't recreate existing tables)
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    print("✅ Tables created!")


if __name__ == "__main__":
    asyncio.run(main())
