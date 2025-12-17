# تست‌نویسی

این سند نحوه نوشتن تست‌ها در فریمورک WeWork را توضیح می‌دهد.

## Unit Tests

```python
import pytest
from src.api.auth_api import get_password_hash, verify_password

def test_password_hashing():
    password = "test123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
```

## Integration Tests

```python
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_login():
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "test123"
    })
    assert response.status_code == 200
```

## مراحل بعدی

- [راهنمای توسعه](./development-guide.md)
- [بهینه‌سازی](./performance.md)

