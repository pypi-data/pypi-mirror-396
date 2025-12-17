"""Event dispatcher using optimized Redis manager for cross-process events."""
import asyncio
from src.core.redis_manager import redis_manager
from src.utils.logging import get_logger

logger = get_logger("event_dispatcher")


class EventDispatcher:
    """Optimized event dispatcher using Redis connection pooling and throttling."""
    
    @classmethod
    async def publish(cls, event_type: str, payload: dict, force: bool = False):
        """Publish event with throttling and batching."""
        success = await redis_manager.publish_event(
            event_type=event_type,
            payload=payload,
            channel='app_events',
            force=force
        )
        
        if success:
            logger.debug("Published event %s", event_type)
        else:
            logger.warning("Failed to publish event %s", event_type)
        
        return success

    @classmethod
    async def subscribe(cls):
        """Subscribe to events channel using optimized connection."""
        # This method is kept for compatibility but uses the old approach
        # In production, consider updating subscribers to use the new manager
        from src.core.redis_manager import RedisPool
        
        pool = RedisPool(redis_manager.redis_url)
        r = await pool.get_connection()
        pub = r.pubsub()
        await pub.subscribe('app_events')
        return pub
