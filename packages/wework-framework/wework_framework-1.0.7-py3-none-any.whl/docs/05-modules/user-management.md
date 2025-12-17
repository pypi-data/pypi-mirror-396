# ماژول مدیریت کاربران

این ماژول مدیریت کاربران، پروفایل و تنظیمات را فراهم می‌کند.

## استفاده

```python
from src.db.models import User
from src.db.base import AsyncSessionLocal
from src.api.auth_api import get_current_active_user

@router.get("/users")
async def list_users(current_user: User = Depends(get_current_active_user)):
    async with AsyncSessionLocal() as session:
        # لیست کاربران
        pass
```

## مراحل بعدی

- [احراز هویت](../02-backend/authentication.md)
- [ماژول پرداخت و بیلینگ](./billing.md)

