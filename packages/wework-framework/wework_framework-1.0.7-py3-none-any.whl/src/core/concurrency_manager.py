"""Concurrency manager for handling distributed locks and event deduplication."""
import asyncio
import hashlib
import json
import time
import uuid
from typing import Optional, Dict, Any
from src.core.redis_manager import redis_manager
from src.utils.logging import get_logger

logger = get_logger("concurrency_manager")


class DistributedLock:
    """Distributed lock using Redis."""
    
    def __init__(self, key: str, timeout: float = 30.0, retry_interval: float = 0.1):
        """
        Initialize distributed lock.
        
        Args:
            key: Lock key in Redis
            timeout: Lock timeout in seconds (auto-release if not released)
            retry_interval: Interval between retry attempts in seconds
        """
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.lock_value = str(uuid.uuid4())
        self.acquired = False
    
    async def acquire(self, wait: bool = True, max_wait: float = 5.0) -> bool:
        """
        Acquire the lock.
        
        Args:
            wait: If True, wait for lock to be available
            max_wait: Maximum time to wait for lock (seconds)
        
        Returns:
            True if lock acquired, False otherwise
        """
        start_time = time.time()
        
        while True:
            try:
                conn = await redis_manager.pool.get_connection()
                # Try to set lock with NX (only if not exists) and EX (expiration)
                result = await conn.set(
                    self.key,
                    self.lock_value,
                    ex=int(self.timeout),
                    nx=True
                )
                
                if result:
                    self.acquired = True
                    logger.debug(f"Lock acquired: {self.key}")
                    return True
                
                if not wait:
                    return False
                
                # Check if we've exceeded max wait time
                if time.time() - start_time >= max_wait:
                    logger.warning(f"Failed to acquire lock {self.key} within {max_wait}s")
                    return False
                
                await asyncio.sleep(self.retry_interval)
                
            except Exception as e:
                logger.error(f"Error acquiring lock {self.key}: {e}")
                if not wait:
                    return False
                await asyncio.sleep(self.retry_interval)
    
    async def release(self) -> bool:
        """
        Release the lock.
        
        Returns:
            True if lock released, False otherwise
        """
        if not self.acquired:
            return False
        
        try:
            conn = await redis_manager.pool.get_connection()
            # Use Lua script to ensure we only delete our own lock
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            result = await conn.eval(lua_script, 1, self.key, self.lock_value)
            
            if result:
                self.acquired = False
                logger.debug(f"Lock released: {self.key}")
                return True
            else:
                logger.warning(f"Lock {self.key} was not owned by this instance")
                return False
                
        except Exception as e:
            logger.error(f"Error releasing lock {self.key}: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.release()


class EventDeduplicator:
    """Prevents duplicate event processing."""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize event deduplicator.
        
        Args:
            ttl: Time to live for event IDs in seconds (default 1 hour)
        """
        self.ttl = ttl
        self._prefix = "event:"
    
    def _generate_event_id(self, event_type: str, payload: Dict[str, Any]) -> str:
        """Generate a unique event ID from event type and payload."""
        # Create a deterministic hash from event type and key payload fields
        key_fields = {}
        
        # For events, use a hash of the entire payload
        # You can customize this based on your event types
        if 'id' in payload:
            key_fields['id'] = payload['id']
        else:
            key_fields = payload
        
        # Create deterministic hash
        event_data = json.dumps({**key_fields, 'type': event_type}, sort_keys=True)
        event_hash = hashlib.sha256(event_data.encode()).hexdigest()
        return f"{event_type}:{event_hash[:16]}"
    
    async def is_duplicate(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Check if event is a duplicate (atomic check-and-set).
        
        Args:
            event_type: Type of event
            payload: Event payload
        
        Returns:
            True if duplicate, False otherwise
        """
        event_id = self._generate_event_id(event_type, payload)
        key = f"{self._prefix}{event_id}"
        
        try:
            conn = await redis_manager.pool.get_connection()
            # Use SET with NX (only if not exists) and EX (expiration) for atomic operation
            # Returns True if key was set (not duplicate), False if key already exists (duplicate)
            result = await conn.set(key, "1", ex=self.ttl, nx=True)
            
            if result:
                # Key was set, meaning this is the first time we see this event
                logger.debug(f"New event processed: {event_id}")
                return False
            else:
                # Key already exists, meaning this is a duplicate
                logger.debug(f"Duplicate event detected: {event_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error checking event duplicate {event_id}: {e}")
            # On error, allow event to proceed (fail open)
            return False
    
    async def mark_processed(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Mark event as processed (alternative to is_duplicate for explicit marking).
        
        Args:
            event_type: Type of event
            payload: Event payload
        
        Returns:
            True if marked successfully
        """
        event_id = self._generate_event_id(event_type, payload)
        key = f"{self._prefix}{event_id}"
        
        try:
            conn = await redis_manager.pool.get_connection()
            await conn.setex(key, self.ttl, "1")
            return True
        except Exception as e:
            logger.error(f"Error marking event as processed {event_id}: {e}")
            return False


class ConcurrencyManager:
    """Main concurrency manager for distributed locks and event deduplication."""
    
    def __init__(self):
        self.deduplicator = EventDeduplicator()
    
    def get_lock(self, key: str, timeout: float = 30.0) -> DistributedLock:
        """
        Get a distributed lock.
        
        Args:
            key: Lock key
            timeout: Lock timeout in seconds
        
        Returns:
            DistributedLock instance
        """
        return DistributedLock(key, timeout=timeout)
    
    async def execute_with_lock(
        self,
        key: str,
        coro,
        timeout: float = 30.0,
        wait: bool = True,
        max_wait: float = 5.0
    ) -> Any:
        """
        Execute a coroutine with a distributed lock.
        
        Args:
            key: Lock key
            coro: Coroutine to execute
            timeout: Lock timeout in seconds
            wait: Whether to wait for lock
            max_wait: Maximum time to wait for lock
        
        Returns:
            Result of coroutine execution, or None if lock not acquired
        """
        lock = self.get_lock(key, timeout)
        
        try:
            acquired = await lock.acquire(wait=wait, max_wait=max_wait)
            if not acquired:
                logger.warning(f"Could not acquire lock {key} for execution")
                return None
            
            return await coro
            
        finally:
            await lock.release()
    
    async def check_event_duplicate(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Check if event is duplicate.
        
        Args:
            event_type: Type of event
            payload: Event payload
        
        Returns:
            True if duplicate, False otherwise
        """
        return await self.deduplicator.is_duplicate(event_type, payload)
    
    async def mark_event_processed(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Mark event as processed.
        
        Args:
            event_type: Type of event
            payload: Event payload
        
        Returns:
            True if marked successfully
        """
        return await self.deduplicator.mark_processed(event_type, payload)


# Global concurrency manager instance
concurrency_manager = ConcurrencyManager()

