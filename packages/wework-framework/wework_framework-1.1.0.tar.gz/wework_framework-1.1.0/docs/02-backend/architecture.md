# معماری بک‌اند

این سند معماری بک‌اند فریمورک WeWork را توضیح می‌دهد.

## معماری کلی

فریمورک WeWork از معماری لایه‌ای (Layered Architecture) استفاده می‌کند:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)          │
│  (Routers, Dependencies, Schemas)   │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│         Business Logic Layer        │
│  (Core Modules, Services, Managers)│
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│         Data Access Layer           │
│  (Models, Repositories, Database)   │
└─────────────────────────────────────┘
```

## لایه‌ها

### 1. API Layer

لایه API که با FastAPI ساخته شده است:

- **Routers**: Endpoint های API
- **Dependencies**: Dependency Injection
- **Schemas**: Pydantic Models برای Validation

```python
# مثال Router
from fastapi import APIRouter, Depends
from src.api.auth_api import get_current_active_user

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/endpoint")
async def endpoint(current_user: User = Depends(get_current_active_user)):
    return {"message": "Hello"}
```

### 2. Business Logic Layer

لایه منطق کسب‌وکار شامل:

- **Core Modules**: ماژول‌های اصلی
- **Services**: سرویس‌های کسب‌وکار
- **Managers**: مدیریت‌کننده‌ها

```python
# مثال Manager
from src.core.redis_manager import redis_manager

class CacheManager:
    async def get(self, key: str):
        return await redis_manager.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600):
        await redis_manager.set(key, value, expire=expire)
```

### 3. Data Access Layer

لایه دسترسی به داده شامل:

- **Models**: SQLAlchemy Models
- **Repositories**: Repository Pattern
- **Database**: Connection و Session Management

```python
# مثال Model
from src.db.base import Base
from sqlalchemy import Column, Integer, String

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

## ماژول‌های اصلی

### Authentication Module

ماژول احراز هویت در `src/api/auth_api.py`:

- JWT Token Management
- Password Hashing
- Role-Based Access Control
- OTP Authentication

### Database Module

ماژول دیتابیس در `src/db/`:

- **base.py**: Base و Session Management
- **models.py**: SQLAlchemy Models
- **repos.py**: Repository Pattern

### Redis Module

ماژول Redis در `src/core/redis_manager.py`:

- Cache Management
- Pub/Sub
- Session Storage

### Event Dispatcher

سیستم رویداد در `src/core/event_dispatcher.py`:

- Event Emission
- Event Handlers
- Async Event Processing

## Dependency Injection

FastAPI از Dependency Injection استفاده می‌کند:

```python
from fastapi import Depends
from src.api.auth_api import get_current_active_user

@router.get("/endpoint")
async def endpoint(current_user: User = Depends(get_current_active_user)):
    # current_user به صورت خودکار inject می‌شود
    return {"user_id": current_user.id}
```

## Async/Await

تمام کدها از async/await استفاده می‌کنند:

```python
async def get_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Item))
        return result.scalars().all()
```

## Error Handling

مدیریت خطا با HTTPException:

```python
from fastapi import HTTPException

@router.get("/item/{item_id}")
async def get_item(item_id: int):
    item = await get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Configuration

تنظیمات در `src/config/settings.py`:

```python
from src.config.settings import settings

# استفاده از تنظیمات
db_url = settings.database_url
jwt_secret = settings.jwt_secret_key
```

## Logging

سیستم Logging در `src/utils/logging.py`:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error message")
```

## Best Practices

1. **Separation of Concerns**: هر لایه مسئولیت مشخص دارد
2. **Dependency Injection**: استفاده از DI برای تست‌پذیری
3. **Async/Await**: استفاده از async برای عملکرد بهتر
4. **Error Handling**: مدیریت صحیح خطاها
5. **Type Hints**: استفاده از Type Hints برای خوانایی بهتر

## مراحل بعدی

- [احراز هویت](./authentication.md)
- [مدیریت دیتابیس](./database.md)
- [API و Routing](./api-routing.md)

