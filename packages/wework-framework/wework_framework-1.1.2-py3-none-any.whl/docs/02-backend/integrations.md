# یکپارچه‌سازی‌ها

این سند یکپارچه‌سازی‌های موجود در فریمورک WeWork را توضیح می‌دهد.

## SMS Integration (WECAN)

### استفاده

```python
from src.integrations.wecan_sms import wecan_sms_client

# ارسال SMS
await wecan_sms_client.send_sms(
    phone_number="09123456789",
    message="کد تایید: 123456",
    template_id=123
)
```

## Web Push

### استفاده

```python
from src.integrations.webpush import send_web_push

await send_web_push(
    subscription={
        "endpoint": "...",
        "keys": {...}
    },
    payload={
        "title": "عنوان",
        "body": "متن"
    }
)
```

## Telegram Bot

### استفاده

```python
from src.telegram.bot import telegram_bot

# ارسال پیام
await telegram_bot.send_message(
    chat_id="...",
    text="پیام"
)
```

## Payment Gateway (Zarinpal)

### استفاده

```python
from src.api.billing_api import create_payment

payment = await create_payment(
    amount=100000,
    description="توضیحات"
)
```

## Best Practices

1. **Error Handling**: خطاهای یکپارچه‌سازی را handle کنید
2. **Configuration**: تنظیمات را در .env قرار دهید
3. **Testing**: در محیط تست از mock استفاده کنید

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [API و Routing](./api-routing.md)

