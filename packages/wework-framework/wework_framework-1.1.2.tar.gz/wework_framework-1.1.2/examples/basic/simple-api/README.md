# مثال: API ساده

این مثال نشان می‌دهد چگونه یک API ساده با Authentication ایجاد کنید.

## ساختار

```
simple-api/
├── backend/            # کد بک‌اند
│   └── api.py
├── frontend/           # کد فرانت‌اند
│   └── Component.jsx
└── README.md
```

## Backend

```python
# backend/api.py
from fastapi import APIRouter, Depends
from src.api.auth_api import get_current_active_user
from src.db.models import User

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/hello")
async def hello():
    return {"message": "Hello from WeWork!"}

@router.get("/protected")
async def protected(current_user: User = Depends(get_current_active_user)):
    return {
        "message": f"Hello {current_user.email}!",
        "user_id": current_user.id
    }
```

## Frontend

```jsx
// frontend/Component.jsx
import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { Button, Card } from '../ui'
import { useAuth } from '../components/AuthContext'

export default function ExampleComponent() {
  const { token } = useAuth()
  const [message, setMessage] = useState('')

  const callPublicAPI = async () => {
    const res = await axios.get(`${API_BASE_URL}/example/hello`)
    setMessage(res.data.message)
  }

  const callProtectedAPI = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/example/protected`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessage(res.data.message)
    } catch (err) {
      setMessage('خطا در احراز هویت')
    }
  }

  return (
    <Card>
      <CardHeader>
        <h2>مثال API</h2>
      </CardHeader>
      <CardBody>
        <Button onClick={callPublicAPI}>API عمومی</Button>
        <Button onClick={callProtectedAPI}>API محافظت شده</Button>
        {message && <p>{message}</p>}
      </CardBody>
    </Card>
  )
}
```

## اجرا

1. Backend را اجرا کنید
2. Frontend را اجرا کنید
3. به صفحه مثال بروید
4. دکمه‌ها را کلیک کنید

