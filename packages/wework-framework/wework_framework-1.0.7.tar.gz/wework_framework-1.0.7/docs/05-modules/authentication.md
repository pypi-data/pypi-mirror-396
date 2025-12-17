# ماژول احراز هویت

برای مستندات کامل احراز هویت، به [مستندات احراز هویت](../02-backend/authentication.md) مراجعه کنید.

## استفاده سریع

```python
from src.api.auth_api import get_current_active_user

@router.get("/protected")
async def endpoint(current_user: User = Depends(get_current_active_user)):
    return {"user_id": current_user.id}
```

## مراحل بعدی

- [احراز هویت کامل](../02-backend/authentication.md)
- [ماژول مدیریت کاربران](./user-management.md)

