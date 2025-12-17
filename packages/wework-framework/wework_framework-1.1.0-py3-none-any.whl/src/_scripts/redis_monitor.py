#!/usr/bin/env python3
"""Redis Performance Monitoring Script

This script monitors Redis performance, memory usage, and connection health.
Run this periodically to track Redis performance and identify issues.

Usage:
    python scripts/redis_monitor.py
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.redis_manager import redis_manager
from src.utils.logging import get_logger

logger = get_logger("redis_monitor")


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


def format_percentage(value: float) -> str:
    """Format percentage with color coding."""
    if value >= 90:
        return f"\033[91m{value:.1f}%\033[0m"  # Red
    elif value >= 75:
        return f"\033[93m{value:.1f}%\033[0m"  # Yellow
    else:
        return f"\033[92m{value:.1f}%\033[0m"  # Green


async def get_redis_info() -> Dict[str, Any]:
    """Get comprehensive Redis information."""
    info = {}
    
    try:
        # Basic Redis info
        memory_info = await redis_manager.get_memory_info()
        if memory_info:
            info.update(memory_info)
        
        # Get connection info
        conn = await redis_manager.pool.get_connection()
        info['connected_clients'] = await conn.info('clients')
        info['total_commands_processed'] = await conn.info('stats')['total_commands_processed']
        info['instantaneous_ops_per_sec'] = await conn.info('stats')['instantaneous_ops_per_sec']
        info['keyspace_hits'] = await conn.info('stats')['keyspace_hits']
        info['keyspace_misses'] = await conn.info('stats')['keyspace_misses']
        
        # Get database info
        db_info = await conn.info('keyspace')
        info['keyspace'] = db_info
        
        # Get configuration
        config_info = await conn.config_get('maxmemory-policy')
        info['maxmemory_policy'] = config_info.get('maxmemory-policy', 'unknown')
        
    except Exception as e:
        logger.error(f"Failed to get Redis info: {e}")
        info['error'] = str(e)
    
    return info


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


async def print_memory_info(info: Dict[str, Any]):
    """Print memory usage information."""
    print_section("Memory Usage")
    
    used_memory = info.get('used_memory', 0)
    max_memory = info.get('maxmemory', 0)
    
    if used_memory and max_memory:
        usage_percent = (used_memory / max_memory) * 100
        print(f"Used Memory:     {format_bytes(used_memory)}")
        print(f"Max Memory:      {format_bytes(max_memory)}")
        print(f"Usage:           {format_percentage(usage_percent)}")
        print(f"Fragmentation:   {info.get('mem_fragmentation_ratio', 'N/A'):.2f}")
    else:
        print(f"Used Memory:     {format_bytes(used_memory) if used_memory else 'N/A'}")
        print(f"Max Memory:      {format_bytes(max_memory) if max_memory else 'N/A'}")
    
    # Keyspace information
    keyspace = info.get('keyspace', {})
    if keyspace:
        print(f"\nDatabase Keyspace:")
        for db, db_info in keyspace.items():
            if isinstance(db_info, dict) and 'keys' in db_info:
                print(f"  {db}: {db_info['keys']} keys, {db_info.get('expires', 'N/A')} expires")


async def print_performance_info(info: Dict[str, Any]):
    """Print performance information."""
    print_section("Performance")
    
    clients = info.get('connected_clients', {})
    print(f"Connected Clients: {clients.get('connected_clients', 'N/A')}")
    print(f"Blocked Clients:   {clients.get('blocked_clients', 'N/A')}")
    
    ops_per_sec = info.get('instantaneous_ops_per_sec', 0)
    print(f"Ops/Second:        {ops_per_sec}")
    
    total_commands = info.get('total_commands_processed', 0)
    print(f"Total Commands:    {total_commands:,}")
    
    # Hit/Miss ratio
    hits = info.get('keyspace_hits', 0)
    misses = info.get('keyspace_misses', 0)
    if hits + misses > 0:
        hit_ratio = (hits / (hits + misses)) * 100
        print(f"Hit Ratio:         {format_percentage(hit_ratio)}")


async def print_redis_manager_stats():
    """Print Redis manager statistics."""
    print_section("Redis Manager Stats")
    
    stats = redis_manager.get_stats()
    print(f"Events Published:  {stats['events_published']:,}")
    print(f"Events Throttled:  {stats['events_throttled']:,}")
    print(f"Events Batched:    {stats['events_batched']:,}")
    print(f"Active Channels:   {stats['active_channels']}")
    print(f"Pool Size:         {stats['pool_size']}")
    
    # Calculate throttling efficiency
    if stats['events_published'] > 0:
        throttling_efficiency = (stats['events_throttled'] / stats['events_published']) * 100
        print(f"Throttling Rate:   {format_percentage(throttling_efficiency)}")


async def print_health_status():
    """Print overall health status."""
    print_section("Health Status")
    
    # Check Redis connection
    is_healthy = await redis_manager.health_check()
    status = "\033[92mHEALTHY\033[0m" if is_healthy else "\033[91mUNHEALTHY\033[0m"
    print(f"Redis Connection:  {status}")
    
    # Memory pressure check
    memory_info = await redis_manager.get_memory_info()
    if memory_info and memory_info.get('used_memory') and memory_info.get('maxmemory'):
        usage_percent = (memory_info['used_memory'] / memory_info['maxmemory']) * 100
        if usage_percent >= 90:
            pressure_status = "\033[91mCRITICAL\033[0m"
        elif usage_percent >= 75:
            pressure_status = "\033[93mWARNING\033[0m"
        else:
            pressure_status = "\033[92mNORMAL\033[0m"
        
        print(f"Memory Pressure:   {pressure_status}")
    
    # Connection pool status
    stats = redis_manager.get_stats()
    active_channels = stats['active_channels']
    if active_channels > 5:
        pool_status = "\033[93mBUSY\033[0m"
    else:
        pool_status = "\033[92mNORMAL\033[0m"
    
    print(f"Connection Pool:   {pool_status}")


async def run_cleanup():
    """Run Redis cleanup operations."""
    print_section("Cleanup Operations")
    
    try:
        await redis_manager.cleanup_expired_data()
        print("✓ Expired data cleanup completed")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")


async def main():
    """Main monitoring function."""
    print_header(f"Redis Performance Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Get Redis information
        info = await get_redis_info()
        
        if 'error' in info:
            print(f"\033[91mERROR:\033[0m {info['error']}")
            return
        
        # Print all sections
        await print_memory_info(info)
        await print_performance_info(info)
        await print_redis_manager_stats()
        await print_health_status()
        
        # Run cleanup if requested
        if len(sys.argv) > 1 and sys.argv[1] == '--cleanup':
            await run_cleanup()
        
        print_header("End of Report")
        
    except Exception as e:
        logger.exception(f"Monitoring failed: {e}")
        print(f"\033[91mMONITORING ERROR:\033[0m {e}")
    
    finally:
        # Close Redis manager
        await redis_manager.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[93mMonitoring interrupted by user\033[0m")
    except Exception as e:
        print(f"\033[91mFatal error:\033[0m {e}")