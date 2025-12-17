# Debugging

این سند نحوه Debug کردن در فریمورک WeWork را توضیح می‌دهد.

## Backend Debugging

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

## Frontend Debugging

```jsx
console.log("Debug message")
console.error("Error message")
```

## مراحل بعدی

- [راهنمای توسعه](./development-guide.md)
- [تست‌نویسی](./testing.md)

