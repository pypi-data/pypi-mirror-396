# پیکربندی اولیه

این راهنما نحوه پیکربندی فریمورک WeWork را توضیح می‌دهد.

## 📝 فایل .env

تمام تنظیمات در فایل `.env` در ریشه پروژه قرار دارد. می‌توانید از `.env.example` کپی کنید:

```bash
cp .env.example .env
```

### تنظیمات ضروری

```env
# ============================================
# Database Configuration
# ============================================
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=wework

# ============================================
# JWT Authentication
# ============================================
JWT_SECRET_KEY=change-this-to-a-random-secret-key-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# ============================================
# Redis Configuration
# ============================================
REDIS_URL=redis://localhost:6379/0

# ============================================
# Frontend Configuration
# ============================================
FRONTEND_BASE_URL=http://localhost:5173
PAYMENT_SUCCESS_PATH=/payment/success
PAYMENT_FAILURE_PATH=/payment/failure
```

### تنظیمات اختیاری

```env
# ============================================
# SMS Integration (WECAN) - Optional
# ============================================
WECAN_REST_URL=https://api.wecan.com
WECAN_TOKEN=your_wecan_token
WECAN_FROM_NUMBER=your_phone_number
WECAN_OTP_TEMPLATE_ID=123

# ============================================
# Web Push (VAPID) - Optional
# ============================================
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_SUBJECT=mailto:admin@example.com

# ============================================
# Payment Gateway (Zarinpal) - Optional
# ============================================
ZARINPAL_MERCHANT_ID=your_merchant_id
ZARINPAL_SANDBOX=true
ZARINPAL_CALLBACK_URL=http://localhost:8000/api/billing/zarinpal/callback

# ============================================
# Logging
# ============================================
LOG_LEVEL=INFO
```

## 🔧 تنظیمات Frontend

فایل `.env` در پوشه `frontend`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_VAPID_PUBLIC_KEY=your_vapid_public_key
```

## 🔐 امنیت

### JWT Secret Key

برای Production، یک Secret Key قوی ایجاد کنید:

```bash
# با Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# یا با OpenSSL
openssl rand -hex 32
```

سپس در `.env` قرار دهید:

```env
JWT_SECRET_KEY=your-generated-secret-key-here
```

### Database Password

مطمئن شوید که رمز عبور دیتابیس قوی است و در `.env` قرار دارد.

## 📊 بررسی تنظیمات

پس از تنظیم `.env`، می‌توانید تنظیمات را بررسی کنید:

```python
# در Python shell
from src.config.settings import settings

print(settings.postgres_host)
print(settings.jwt_secret_key)
print(settings.redis_url)
```

## 🐳 تنظیمات Docker

اگر از Docker استفاده می‌کنید، تنظیمات در `docker-compose.yml` و `.env` قرار دارد.

## 🔄 تغییر تنظیمات

پس از تغییر `.env`:
- بک‌اند را restart کنید
- فرانت‌اند را restart کنید (اگر تنظیمات frontend تغییر کرده)

## 📚 مراحل بعدی

- [راهنمای نصب](./installation.md) - راه‌اندازی کامل
- [راهنمای سریع](./quickstart.md) - شروع سریع
- [ساختار پروژه](./project-structure.md) - ساختار فایل‌ها

---

**نکته**: هرگز فایل `.env` را در Git commit نکنید. از `.env.example` برای نمونه استفاده کنید.
