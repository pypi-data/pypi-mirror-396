# مدیریت رویدادها

این سند نحوه استفاده از Event Dispatcher در فریمورک WeWork را توضیح می‌دهد.

## Event Dispatcher

### استفاده پایه

```python
from src.core.event_dispatcher import event_dispatcher

# ثبت Event Handler
@event_dispatcher.on("user.created")
async def handle_user_created(event_data):
    print(f"User created: {event_data['user_id']}")

# ارسال Event
await event_dispatcher.emit("user.created", {
    "user_id": 123,
    "email": "user@example.com"
})
```

## ثبت Event Handlers

### Decorator

```python
@event_dispatcher.on("order.placed")
async def handle_order_placed(event_data):
    order_id = event_data['order_id']
    # پردازش سفارش
    pass
```

### Manual Registration

```python
async def handle_payment(event_data):
    # پردازش پرداخت
    pass

event_dispatcher.register("payment.completed", handle_payment)
```

## ارسال Events

### Simple Event

```python
await event_dispatcher.emit("user.updated", {
    "user_id": 123,
    "changes": ["email", "name"]
})
```

### Event با Priority

```python
await event_dispatcher.emit("order.created", {
    "order_id": 456
}, priority="high")
```

## Event Patterns

### Before/After Events

```python
@event_dispatcher.on("user.create.before")
async def validate_user(event_data):
    # Validation
    pass

@event_dispatcher.on("user.create.after")
async def send_welcome_email(event_data):
    # Send email
    pass
```

### Chain Events

```python
@event_dispatcher.on("order.created")
async def process_order(event_data):
    # Process order
    await event_dispatcher.emit("order.processed", event_data)
```

## Error Handling

```python
@event_dispatcher.on("user.created")
async def handle_user_created(event_data):
    try:
        # پردازش
        pass
    except Exception as e:
        # Log error
        logger.error(f"Error handling user.created: {e}")
```

## Best Practices

1. **Event Naming**: از pattern مشخص استفاده کنید (`entity.action`)
2. **Async Handlers**: همیشه از async استفاده کنید
3. **Error Handling**: خطاها را handle کنید
4. **Documentation**: Event ها را مستند کنید

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [مدیریت کارها و Background Jobs](./tasks-jobs.md)

