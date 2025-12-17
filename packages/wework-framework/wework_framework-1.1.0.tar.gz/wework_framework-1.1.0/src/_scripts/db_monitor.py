#!/usr/bin/env python3
import asyncio
import logging
from datetime import datetime
from src.db.base import engine
from sqlalchemy import text
from pathlib import Path

# تنظیم logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def monitor_database():
    """Monitor database health and table existence"""
    try:
        async with engine.connect() as conn:
            # Check connection
            await conn.execute(text("SELECT 1"))
            
            # Check table count
            result = await conn.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            
            # Get list of all tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # Log current status
            timestamp = datetime.now().isoformat()
            logger.info(f"[{timestamp}] Database Status:")
            logger.info(f"  📊 Tables: {table_count}")
            logger.info(f"  📋 Table List: {', '.join(tables)}")
            
            # Check for critical tables
            critical_tables = [
                'users', 'subscription_plans', 'user_subscriptions', 
                'payments', 'notifications', 'config_kv'
            ]
            
            missing_critical = [t for t in critical_tables if t not in tables]
            if missing_critical:
                logger.error(f"🚨 Missing critical tables: {missing_critical}")
                logger.error("🚨 Possible data loss detected!")
                return False
            
            logger.info("✅ All critical tables present")
            
            # Check data integrity
            try:
                # Check user count
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                logger.info(f"👥 User count: {user_count}")
                
                # Check strategy count
                result = await conn.execute(text("SELECT COUNT(*) FROM strategies"))
                strategy_count = result.scalar()
                logger.info(f"🧠 Strategy count: {strategy_count}")
                
                # Check bot count
                result = await conn.execute(text("SELECT COUNT(*) FROM trading_bots"))
                bot_count = result.scalar()
                logger.info(f"🤖 Trading bot count: {bot_count}")
                
            except Exception as e:
                logger.warning(f"⚠️ Data integrity check failed: {e}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database monitoring failed: {e}")
        logger.error("❌ Database connection lost!")
        return False

async def check_backup_status():
    """Check backup directory and recent backups"""
    backup_dir = Path("backups")
    if not backup_dir.exists():
        logger.warning("⚠️ Backup directory does not exist")
        return False
    
    backups = list(backup_dir.glob("backup_*.sql"))
    if not backups:
        logger.warning("⚠️ No backups found")
        return False
    
    # Sort by modification time
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_backup = backups[0]
    
    # Check if latest backup is recent (within 24 hours)
    import time
    current_time = time.time()
    backup_time = latest_backup.stat().st_mtime
    
    hours_old = (current_time - backup_time) / 3600
    
    if hours_old < 24:
        logger.info(f"✅ Latest backup is recent: {latest_backup.name} ({hours_old:.1f} hours old)")
        return True
    else:
        logger.warning(f"⚠️ Latest backup is old: {latest_backup.name} ({hours_old:.1f} hours old)")
        return False

async def main():
    """Main monitoring function"""
    logger.info("🔍 Starting Database Health Monitoring")
    logger.info("=" * 50)
    
    # Check database health
    db_healthy = await monitor_database()
    
    # Check backup status
    backup_ok = await check_backup_status()
    
    # Final status
    logger.info("=" * 50)
    if db_healthy and backup_ok:
        logger.info("✅ All systems healthy")
    else:
        if not db_healthy:
            logger.error("❌ Database issues detected")
        if not backup_ok:
            logger.error("❌ Backup issues detected")
        logger.error("🚨 Action required!")

if __name__ == "__main__":
    asyncio.run(main())