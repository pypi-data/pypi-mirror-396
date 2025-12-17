#!/usr/bin/env python3
"""
Database Backup and Recovery Script
This script helps prevent data loss by creating regular backups
"""

import asyncio
import os
import subprocess
import datetime
from pathlib import Path
from src.config.settings import settings

async def create_database_backup():
    """Create a backup of the database"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f"backup_{timestamp}.sql"
    
    # Extract connection details from database URL
    db_url = settings.database_url
    if "postgresql+asyncpg://" in db_url:
        # Convert asyncpg URL to regular postgres URL
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Create backup using pg_dump
    try:
        cmd = [
            "pg_dump",
            "-h", settings.postgres_host,
            "-U", settings.postgres_user,
            "-d", settings.postgres_db,
            "-f", str(backup_file)
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.postgres_password
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Database backup created: {backup_file}")
            return str(backup_file)
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

async def restore_database_backup(backup_file):
    """Restore database from backup"""
    try:
        # Extract connection details
        cmd = [
            "psql",
            "-h", settings.postgres_host,
            "-U", settings.postgres_user,
            "-d", settings.postgres_db,
            "-f", backup_file
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.postgres_password
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Database restored from: {backup_file}")
            return True
        else:
            print(f"❌ Restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error restoring backup: {e}")
        return False

async def check_database_health():
    """Check database connectivity and basic operations"""
    try:
        from src.db.base import engine
        from sqlalchemy import text
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection is healthy")
            
            # Check table count
            result = await conn.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"📊 Current table count: {table_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False

async def main():
    """Main backup management function"""
    print("🗄️ Database Backup Management")
    print("=" * 40)
    
    # Check database health
    await check_database_health()
    
    # Create backup
    backup_file = await create_database_backup()
    
    if backup_file:
        print(f"💾 Backup available at: {backup_file}")
        
        # List all backups
        backup_dir = Path("backups")
        if backup_dir.exists():
            backups = list(backup_dir.glob("backup_*.sql"))
            print(f"📁 Total backups: {len(backups)}")
            
            # Clean old backups (keep last 10)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            if len(backups) > 10:
                for old_backup in backups[10:]:
                    old_backup.unlink()
                    print(f"🗑️ Removed old backup: {old_backup.name}")

if __name__ == "__main__":
    asyncio.run(main())