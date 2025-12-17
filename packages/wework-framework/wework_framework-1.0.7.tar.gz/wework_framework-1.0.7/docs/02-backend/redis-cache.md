# مدیریت Redis و Cache

این سند نحوه استفاده از Redis و Cache در فریمورک WeWork را توضیح می‌دهد.

## Redis Manager

### استفاده پایه

```python
from src.core.redis_manager import redis_manager

# ذخیره داده
await redis_manager.set("key", "value", expire=3600)

# دریافت داده
value = await redis_manager.get("key")

# حذف داده
await redis_manager.delete("key")
```

## Cache Patterns

### Cache-Aside Pattern

```python
async def get_item(item_id: int):
    # بررسی Cache
    cached = await redis_manager.get(f"item:{item_id}")
    if cached:
        return json.loads(cached)
    
    # دریافت از دیتابیس
    item = await get_item_from_db(item_id)
    
    # ذخیره در Cache
    await redis_manager.set(
        f"item:{item_id}",
        json.dumps(item),
        expire=3600
    )
    
    return item
```

### Cache-Through Pattern

```python
async def get_or_set(key: str, fetch_func, expire: int = 3600):
    cached = await redis_manager.get(key)
    if cached:
        return json.loads(cached)
    
    data = await fetch_func()
    await redis_manager.set(key, json.dumps(data), expire=expire)
    return data
```

## Pub/Sub

### Publish

```python
await redis_manager.publish("channel", {"message": "Hello"})
```

### Subscribe

```python
async def subscribe_to_channel(channel: str):
    async for message in redis_manager.subscribe(channel):
        # پردازش پیام
        print(message)
```

## Session Management

```python
# ذخیره Session
await redis_manager.set(
    f"session:{session_id}",
    json.dumps(user_data),
    expire=86400  # 24 hours
)

# دریافت Session
session_data = await redis_manager.get(f"session:{session_id}")
```

## Rate Limiting

```python
async def rate_limit(key: str, limit: int = 10, window: int = 60):
    current = await redis_manager.get(f"rate:{key}")
    if current and int(current) >= limit:
        raise HTTPException(429, "Rate limit exceeded")
    
    await redis_manager.incr(f"rate:{key}")
    await redis_manager.expire(f"rate:{key}", window)
```

## Best Practices

1. **Key Naming**: از pattern مشخص استفاده کنید (`module:entity:id`)
2. **Expiration**: همیشه expire time تنظیم کنید
3. **Serialization**: از JSON برای داده‌های پیچیده استفاده کنید
4. **Error Handling**: خطاهای Redis را handle کنید

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [مدیریت رویدادها](./events.md)

