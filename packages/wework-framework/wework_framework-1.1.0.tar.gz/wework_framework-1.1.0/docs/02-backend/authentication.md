# احراز هویت و مدیریت کاربران

سیستم احراز هویت فریمورک WeWork یک سیستم کامل و آماده برای استفاده است که شامل ثبت‌نام، ورود، مدیریت نقش‌ها و OTP می‌شود.

## معماری

سیستم احراز هویت بر اساس JWT (JSON Web Tokens) ساخته شده است:

- **JWT Tokens**: برای احراز هویت کاربران
- **Password Hashing**: استفاده از bcrypt برای هش کردن رمز عبور
- **Role-Based Access Control**: مدیریت دسترسی بر اساس نقش
- **OTP Authentication**: ورود با کد یکبار مصرف

## استفاده پایه

### ثبت‌نام کاربر

```python
from src.api.auth_api import router, UserCreate
from fastapi import APIRouter

# استفاده از endpoint موجود
# POST /api/auth/register
{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "نام کاربر",
    "phone_number": "09123456789"  # اختیاری
}
```

### ورود کاربر

```python
# POST /api/auth/login
# استفاده از OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordRequestForm

form_data = OAuth2PasswordRequestForm(
    username="user@example.com",  # email
    password="secure_password"
)

# Response:
{
    "access_token": "eyJ...",
    "token_type": "bearer"
}
```

### دریافت اطلاعات کاربر فعلی

```python
from src.api.auth_api import get_current_active_user
from src.db.models import User

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }
```

## Dependencies

### get_current_user

دریافت کاربر از توکن JWT (بدون بررسی فعال بودن).

```python
from src.api.auth_api import get_current_user

@router.get("/endpoint")
async def my_endpoint(current_user: User = Depends(get_current_user)):
    # کاربر می‌تواند غیرفعال باشد
    return {"user_id": current_user.id}
```

### get_current_active_user

دریافت کاربر فعال از توکن JWT.

```python
from src.api.auth_api import get_current_active_user

@router.get("/endpoint")
async def my_endpoint(current_user: User = Depends(get_current_active_user)):
    # فقط کاربران فعال
    return {"user_id": current_user.id}
```

### get_current_admin

دریافت کاربر با نقش admin یا super_admin.

```python
from src.api.auth_api import get_current_admin

@router.get("/admin/endpoint")
async def admin_endpoint(admin: User = Depends(get_current_admin)):
    # فقط ادمین‌ها
    return {"message": "Admin only"}
```

### get_current_super_admin

دریافت کاربر با نقش super_admin.

```python
from src.api.auth_api import get_current_super_admin

@router.get("/super-admin/endpoint")
async def super_admin_endpoint(super_admin: User = Depends(get_current_super_admin)):
    # فقط سوپر ادمین
    return {"message": "Super admin only"}
```

## مدیریت نقش‌ها

### نقش‌های موجود

- **user**: کاربر عادی
- **admin**: ادمین
- **super_admin**: سوپر ادمین

### بررسی نقش

```python
from src.api.auth_api import is_admin_or_super_admin, is_super_admin

@router.get("/endpoint")
async def my_endpoint(current_user: User = Depends(get_current_active_user)):
    if is_admin_or_super_admin(current_user):
        # کد ادمین
        pass
    
    if is_super_admin(current_user):
        # کد سوپر ادمین
        pass
```

## OTP Authentication

### درخواست OTP

```python
# POST /api/auth/request-otp
{
    "phone_number": "09123456789",
    "full_name": "نام کاربر"  # اختیاری
}

# Response:
{
    "sent": true,
    "expires_in": 300,
    "is_new_user": false
}
```

### ورود با OTP

```python
# POST /api/auth/login-otp
{
    "phone_number": "09123456789",
    "code": "123456",
    "full_name": "نام کاربر"  # اختیاری
}

# Response:
{
    "access_token": "eyJ...",
    "token_type": "bearer"
}
```

## مدیریت پروفایل

### دریافت پروفایل

```python
# GET /api/auth/me
# نیاز به Authentication

# Response:
{
    "id": 1,
    "email": "user@example.com",
    "phone_number": "09123456789",
    "full_name": "نام کاربر",
    "username": "username",
    "bio": "بیوگرافی",
    "avatar": "url",
    "role": {
        "name": "user",
        "title": "کاربر"
    },
    "is_active": true
}
```

### به‌روزرسانی پروفایل

```python
# PATCH /api/auth/me
{
    "full_name": "نام جدید",
    "username": "new_username",  # فقط یکبار قابل تنظیم
    "bio": "بیوگرافی جدید",
    "avatar": "url"
}
```

### پروفایل عمومی

```python
# GET /api/auth/users/{user_id}/public
# بدون نیاز به Authentication

# GET /api/auth/users/username/{username}/public
# بدون نیاز به Authentication
```

## تنظیمات Telegram

### دریافت تنظیمات

```python
# GET /api/auth/me/telegram

# Response:
{
    "telegram_enabled": true,
    "telegram_bot_token": "token",
    "telegram_chat_id": "chat_id"
}
```

### به‌روزرسانی تنظیمات

```python
# PATCH /api/auth/me/telegram
{
    "telegram_enabled": true,
    "telegram_bot_token": "token",
    "telegram_chat_id": "chat_id"
}
```

## Utilities

### ایجاد توکن دسترسی

```python
from src.api.auth_api import create_access_token

token = create_access_token(
    data={"sub": user.id, "role": user.role},
    expires_delta=timedelta(hours=24)
)
```

### Hash کردن رمز عبور

```python
from src.api.auth_api import get_password_hash, verify_password

# Hash کردن
hashed = get_password_hash("password123")

# بررسی
is_valid = verify_password("password123", hashed)
```

### دریافت کاربر

```python
from src.api.auth_api import get_user_by_email, get_user_by_phone, get_user_by_id

# با ایمیل
user = await get_user_by_email("user@example.com")

# با شماره تلفن
user = await get_user_by_phone("09123456789")

# با ID
user = await get_user_by_id(1)
```

## مثال کامل: API با Authentication

```python
from fastapi import APIRouter, Depends, HTTPException
from src.api.auth_api import get_current_active_user, get_current_admin
from src.db.models import User
from src.db.base import AsyncSessionLocal
from sqlalchemy import select

router = APIRouter(prefix="/api/my", tags=["my"])

# Endpoint عمومی
@router.get("/public")
async def public_endpoint():
    return {"message": "Public endpoint"}

# Endpoint نیازمند Authentication
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    return {
        "message": "Protected endpoint",
        "user_id": current_user.id,
        "email": current_user.email
    }

# Endpoint نیازمند Admin
@router.get("/admin-only")
async def admin_endpoint(admin: User = Depends(get_current_admin)):
    return {
        "message": "Admin only endpoint",
        "admin_id": admin.id
    }

# Endpoint با بررسی نقش سفارشی
@router.get("/custom-role")
async def custom_role_endpoint(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"message": "Custom role endpoint"}
```

## Frontend Integration

### استفاده در React

```jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'

function useAuth() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  
  useEffect(() => {
    if (token) {
      fetchUser()
    }
  }, [token])
  
  const fetchUser = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(res.data)
    } catch (err) {
      setToken(null)
      localStorage.removeItem('token')
    }
  }
  
  const login = async (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const res = await axios.post(`${API_BASE_URL}/auth/login`, formData)
    setToken(res.data.access_token)
    localStorage.setItem('token', res.data.access_token)
    await fetchUser()
  }
  
  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
  }
  
  return { user, token, login, logout, fetchUser }
}
```

## امنیت

### Best Practices

1. **همیشه از HTTPS استفاده کنید**: در Production
2. **JWT Secret قوی**: از یک secret key قوی استفاده کنید
3. **Expiration Time**: توکن‌ها را با زمان انقضا محدود کنید
4. **Password Policy**: قوانین قوی برای رمز عبور
5. **Rate Limiting**: محدود کردن تعداد درخواست‌ها

### تنظیمات امنیتی

```python
# در .env
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [API و Routing](./api-routing.md)
- [مدیریت دیتابیس](./database.md)

