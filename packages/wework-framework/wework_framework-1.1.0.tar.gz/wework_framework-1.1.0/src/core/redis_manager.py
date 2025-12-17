"""Optimized Redis connection manager with pooling, throttling, and performance monitoring."""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
import redis.asyncio as aioredis
from collections import deque

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger("redis_manager")


class RedisPool:
    """Redis connection pool with health monitoring."""
    
    def __init__(self, redis_url: str, pool_size: int = 10):
        self.redis_url = redis_url
        self.pool_size = pool_size
        self._pool: Optional[aioredis.Redis] = None
        self._lock = asyncio.Lock()
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
        
    async def get_connection(self) -> aioredis.Redis:
        """Get Redis connection from pool."""
        async with self._lock:
            if self._pool is None:
                self._pool = aioredis.ConnectionPool.from_url(
                    self.redis_url,
                    max_connections=self.pool_size,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={}
                )
            return aioredis.Redis(connection_pool=self._pool)
    
    async def close(self):
        """Close Redis connection pool."""
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        current_time = time.time()
        if current_time - self._last_health_check < self._health_check_interval:
            return True
        
        try:
            conn = await self.get_connection()
            await conn.ping()
            self._last_health_check = current_time
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


class EventThrottler:
    """Throttles high-frequency events to reduce Redis load."""
    
    def __init__(self):
        self._event_queues: Dict[str, deque] = {}
        self._last_flush: Dict[str, float] = {}
        self._flush_interval = 2.0  # seconds
        
    def add_event(self, channel: str, event_type: str, payload: dict) -> bool:
        """Add event to throttling queue. Returns True if event should be queued."""
        current_time = time.time()
        
        if channel not in self._event_queues:
            self._event_queues[channel] = deque()
            self._last_flush[channel] = current_time
        
        # Don't queue too many events for the same channel
        if len(self._event_queues[channel]) > 50:
            return False
        
        self._event_queues[channel].append({
            'type': event_type,
            'payload': payload,
            'timestamp': current_time
        })
        
        # Always allow critical events (errors, etc.)
        if event_type in ['error', 'critical']:
            return True
            
        # Throttle non-critical events
        return len(self._event_queues[channel]) >= 10 or \
               (current_time - self._last_flush[channel]) >= self._flush_interval
    
    def should_flush(self, channel: str) -> bool:
        """Check if channel should be flushed."""
        current_time = time.time()
        if channel not in self._event_queues:
            return False
            
        return (len(self._event_queues[channel]) >= 10) or \
               (current_time - self._last_flush[channel]) >= self._flush_interval
    
    def get_events(self, channel: str) -> List[dict]:
        """Get and clear events for channel."""
        if channel not in self._event_queues:
            return []
            
        events = list(self._event_queues[channel])
        self._event_queues[channel].clear()
        self._last_flush[channel] = time.time()
        return events
    
    def cleanup_old_events(self, max_age: int = 300):
        """Clean up old events from all channels."""
        current_time = time.time()
        for channel in list(self._event_queues.keys()):
            queue = self._event_queues[channel]
            # Remove events older than max_age
            while queue and (current_time - queue[0]['timestamp']) > max_age:
                queue.popleft()
            
            # Remove empty queues
            if not queue:
                del self._event_queues[channel]
                del self._last_flush[channel]


class OptimizedRedisManager:
    """Optimized Redis manager with connection pooling, throttling, and monitoring."""
    
    def __init__(self):
        self.redis_url = settings.redis_url
        self.pool = RedisPool(self.redis_url, pool_size=10)
        self.throttler = EventThrottler()
        self._stats = {
            'events_published': 0,
            'events_throttled': 0,
            'events_batched': 0,
            'connections_created': 0,
            'last_health_check': 0
        }
        self._flush_tasks: Dict[str, asyncio.Task] = {}
        
    async def publish_event(self, event_type: str, payload: dict, 
                          channel: str = 'app_events', force: bool = False) -> bool:
        """Publish event with optional throttling."""
        try:
            # Check if event should be throttled
            should_queue = not force and not self.throttler.add_event(channel, event_type, payload)
            
            if should_queue:
                self._stats['events_throttled'] += 1
                logger.debug(f"Event {event_type} throttled for channel {channel}")
                return True
            
            self._stats['events_published'] += 1
            
            # For critical events or when queue is full, publish immediately
            if force or event_type in ['error', 'critical'] or \
               len(self.throttler._event_queues.get(channel, [])) >= 10:
                return await self._publish_immediate(channel, event_type, payload)
            
            # Start flush task for channel if not already running
            if channel not in self._flush_tasks or self._flush_tasks[channel].done():
                self._flush_tasks[channel] = asyncio.create_task(
                    self._periodic_flush(channel)
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False
    
    async def _publish_immediate(self, channel: str, event_type: str, payload: dict) -> bool:
        """Publish event immediately to Redis."""
        try:
            conn = await self.pool.get_connection()
            message = json.dumps({'type': event_type, 'payload': payload})
            await conn.publish(channel, message)
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
            return False
    
    async def _periodic_flush(self, channel: str):
        """Periodically flush events for a channel."""
        try:
            while True:
                await asyncio.sleep(1.0)  # Check every second
                
                if self.throttler.should_flush(channel):
                    events = self.throttler.get_events(channel)
                    if events:
                        await self._batch_publish(channel, events)
                        
        except asyncio.CancelledError:
            # Flush remaining events on cancellation
            events = self.throttler.get_events(channel)
            if events:
                await self._batch_publish(channel, events)
        except Exception as e:
            logger.error(f"Error in periodic flush for {channel}: {e}")
    
    async def _batch_publish(self, channel: str, events: List[dict]):
        """Batch publish events to reduce Redis connections."""
        if not events:
            return
            
        try:
            conn = await self.pool.get_connection()
            
            # Batch publish all events
            async with conn.pipeline() as pipe:
                for event in events:
                    message = json.dumps({
                        'type': event['type'],
                        'payload': event['payload']
                    })
                    pipe.publish(channel, message)
                
                await pipe.execute()
                self._stats['events_batched'] += len(events)
                
            logger.debug(f"Batched {len(events)} events for channel {channel}")
            
        except Exception as e:
            logger.error(f"Failed to batch publish events: {e}")
    
    async def store_hash(self, name: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis hash with optional TTL."""
        try:
            conn = await self.pool.get_connection()
            await conn.hset(name, key, json.dumps(value))
            
            if ttl:
                await conn.expire(name, ttl)
                
            return True
        except Exception as e:
            logger.error(f"Failed to store hash {name}:{key}: {e}")
            return False
    
    async def get_hash(self, name: str, key: str) -> Optional[Any]:
        """Get value from Redis hash."""
        try:
            conn = await self.pool.get_connection()
            value = await conn.hget(name, key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Failed to get hash {name}:{key}: {e}")
            return None
    
    async def delete_hash_key(self, name: str, key: str) -> bool:
        """Delete key from Redis hash."""
        try:
            conn = await self.pool.get_connection()
            await conn.hdel(name, key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete hash key {name}:{key}: {e}")
            return False
    
    async def get_memory_info(self) -> Optional[dict]:
        """Get Redis memory information."""
        try:
            conn = await self.pool.get_connection()
            info = await conn.info('memory')
            return {
                'used_memory': info.get('used_memory'),
                'used_memory_human': info.get('used_memory_human'),
                'maxmemory': info.get('maxmemory'),
                'mem_fragmentation_ratio': info.get('mem_fragmentation_ratio'),
                'connected_clients': info.get('connected_clients')
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return None
    
    async def cleanup_expired_data(self):
        """Clean up expired data and old events."""
        try:
            # Clean up old throttled events
            self.throttler.cleanup_old_events()
            
            # Clean up old event message mappings (keep last 1000)
            conn = await self.pool.get_connection()
            event_count = await conn.hlen('event_msg_map')
            
            if event_count > 1000:
                # Keep only the most recent 1000 entries
                keys = await conn.hkeys('event_msg_map')
                keys_to_delete = keys[:-1000]  # Keep last 1000
                if keys_to_delete:
                    await conn.hdel('event_msg_map', *keys_to_delete)
                    logger.info(f"Cleaned up {len(keys_to_delete)} old event message mappings")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
    
    def get_stats(self) -> dict:
        """Get Redis manager statistics."""
        return {
            **self._stats,
            'active_channels': len(self.throttler._event_queues),
            'pool_size': self.pool.pool_size
        }
    
    async def health_check(self) -> bool:
        """Perform health check on Redis connection."""
        return await self.pool.health_check()
    
    async def close(self):
        """Close Redis manager and cleanup resources."""
        # Cancel all flush tasks
        for task in self._flush_tasks.values():
            task.cancel()
        
        if self._flush_tasks:
            await asyncio.gather(*self._flush_tasks.values(), return_exceptions=True)
        
        # Close connection pool
        await self.pool.close()
        
        logger.info("Redis manager closed")


# Global Redis manager instance
redis_manager = OptimizedRedisManager()