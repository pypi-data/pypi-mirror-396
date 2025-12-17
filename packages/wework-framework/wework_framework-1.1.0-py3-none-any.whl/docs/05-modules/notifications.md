# ماژول اعلان‌رسانی

این ماژول سیستم اعلان‌رسانی از طریق SMS، Web Push و Telegram را فراهم می‌کند.

## استفاده

```python
from src.api.notifications_api import send_notification

await send_notification(
    user_id=123,
    title="عنوان",
    message="پیام"
)
```

## مراحل بعدی

- [یکپارچه‌سازی‌ها](../02-backend/integrations.md)

