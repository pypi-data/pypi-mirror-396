# ماژول پرداخت و بیلینگ

این ماژول سیستم پرداخت و مدیریت اشتراک را فراهم می‌کند.

## استفاده

```python
from src.api.billing_api import create_payment

payment = await create_payment(
    amount=100000,
    description="اشتراک ماهانه"
)
```

## مراحل بعدی

- [ماژول اعلان‌رسانی](./notifications.md)

