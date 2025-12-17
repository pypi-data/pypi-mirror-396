# مثال‌های یکپارچه‌سازی

این بخش شامل مثال‌های یکپارچه‌سازی با سرویس‌های خارجی است.

## SMS Integration

```python
from src.integrations.wecan_sms import wecan_sms_client

await wecan_sms_client.send_sms(
    phone_number="09123456789",
    message="کد تایید: 123456"
)
```

## Payment Integration

```python
from src.api.billing_api import create_payment

payment = await create_payment(
    amount=100000,
    description="پرداخت"
)
```

## مراحل بعدی

- [مثال‌های پایه](./basic-examples.md)
- [مثال‌های پیشرفته](./advanced-examples.md)

