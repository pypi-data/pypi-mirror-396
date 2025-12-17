# Authentication API

## POST /api/auth/register

ثبت‌نام کاربر جدید.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "نام کاربر"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "نام کاربر"
}
```

## POST /api/auth/login

ورود کاربر.

**Request:**
```
username: user@example.com
password: password123
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

## GET /api/auth/me

دریافت اطلاعات کاربر فعلی.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "نام کاربر"
}
```

## مراحل بعدی

- [User Management API](./user-management.md)
- [Billing API](./billing.md)

