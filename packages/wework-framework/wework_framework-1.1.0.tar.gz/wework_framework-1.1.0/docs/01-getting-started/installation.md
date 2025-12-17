# نصب و راه‌اندازی

این راهنما شما را در نصب و راه‌اندازی فریمورک WeWork راهنمایی می‌کند.

## ⚡ راه‌اندازی سریع (5 دقیقه)

### با Docker (توصیه می‌شود)

```bash
# 1. کلون کردن پروژه
git clone https://github.com/wecanco/WeWork.git
cd wework-framework

# 2. ایجاد فایل .env
cp .env.example .env
# فایل .env را ویرایش کنید

# 3. راه‌اندازی همه سرویس‌ها
docker-compose up -d

# 4. ایجاد جداول دیتابیس
docker-compose exec api python -m src.db.create_tables

# 5. ایجاد کاربر ادمین اولیه (اختیاری)
docker-compose exec api python -c "
from src.db.base import AsyncSessionLocal
from src.db.models import User
from src.api.auth_api import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as session:
        admin = User(
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            role='super_admin',
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print('Admin user created!')

asyncio.run(create_admin())
"
```

✅ **تمام!** حالا می‌توانید به آدرس‌های زیر دسترسی داشته باشید:
- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

### بدون Docker

```bash
# 1. کلون کردن پروژه
git clone https://github.com/wecanco/WeWork.git
cd wework-framework

# 2. نصب وابستگی‌های Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. راه‌اندازی PostgreSQL و Redis
# PostgreSQL و Redis باید نصب و در حال اجرا باشند

# 4. ایجاد فایل .env
cp .env.example .env
# فایل .env را ویرایش کنید

# 5. ایجاد جداول دیتابیس
python -m src.db.create_tables

# 6. راه‌اندازی بک‌اند
uvicorn src.api.app:app --reload --port 8000

# 7. در ترمینال جدید - راه‌اندازی فرانت‌اند
cd frontend
npm install
npm run dev
```

## 📋 پیش‌نیازها

قبل از شروع، مطمئن شوید که موارد زیر را نصب کرده‌اید:

- **Python 3.9+**: برای بک‌اند
- **Node.js 18+**: برای فرانت‌اند
- **PostgreSQL 12+**: برای دیتابیس
- **Redis 6+**: برای Cache و Pub/Sub
- **Docker** (اختیاری): برای استقرار با Docker

## 🔧 تنظیمات

### فایل .env

یک فایل `.env` در ریشه پروژه ایجاد کنید:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=wework

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis
REDIS_URL=redis://localhost:6379/0

# Frontend
FRONTEND_BASE_URL=http://localhost:5173

# Optional: SMS Integration (WECAN)
WECAN_REST_URL=https://api.wecan.com
WECAN_TOKEN=your_token
WECAN_FROM_NUMBER=your_number
WECAN_OTP_TEMPLATE_ID=123

# Optional: Web Push (VAPID)
VAPID_PUBLIC_KEY=your_public_key
VAPID_PRIVATE_KEY=your_private_key
VAPID_SUBJECT=mailto:admin@example.com

# Optional: Payment Gateway (Zarinpal)
ZARINPAL_MERCHANT_ID=your_merchant_id
ZARINPAL_SANDBOX=true
ZARINPAL_CALLBACK_URL=http://localhost:8000/api/billing/zarinpal/callback
```

### فایل .env در Frontend

یک فایل `.env` در پوشه `frontend` ایجاد کنید:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_VAPID_PUBLIC_KEY=your_vapid_public_key
```

## 🗄️ راه‌اندازی دیتابیس

### ایجاد جداول

```bash
# با Docker
docker-compose exec api python -m src.db.create_tables

# بدون Docker
python -m src.db.create_tables
```

### Seed کردن داده‌های اولیه (اختیاری)

```bash
# Seed کردن پلن‌های اشتراک
python -m src.db.seed_subscription_plans
```

## 👤 ایجاد کاربر اولیه

### با Python Script

```python
# create_admin.py
from src.db.base import AsyncSessionLocal
from src.db.models import User
from src.api.auth_api import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as session:
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role="super_admin",
            is_active=True,
            full_name="Admin User"
        )
        session.add(admin)
        await session.commit()
        print("✅ Admin user created!")
        print("Email: admin@example.com")
        print("Password: admin123")

if __name__ == "__main__":
    asyncio.run(create_admin())
```

اجرا:

```bash
python create_admin.py
```

### با Docker

```bash
docker-compose exec api python create_admin.py
```

## ✅ بررسی نصب

پس از راه‌اندازی، می‌توانید موارد زیر را بررسی کنید:

1. **بک‌اند**: http://localhost:8000/docs - مستندات Swagger
2. **فرانت‌اند**: http://localhost:5173 - رابط کاربری
3. **Health Check**: http://localhost:8000/ - صفحه اصلی API

## 🐳 استفاده از Docker

### راه‌اندازی کامل

```bash
# راه‌اندازی همه سرویس‌ها
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f

# توقف سرویس‌ها
docker-compose down

# توقف و حذف volume ها
docker-compose down -v
```

### دسترسی به Container

```bash
# دسترسی به بک‌اند
docker-compose exec api bash

# اجرای دستورات Python
docker-compose exec api python -m src.db.create_tables

# مشاهده لاگ‌های بک‌اند
docker-compose logs -f api
```

## 🔍 عیب‌یابی

### مشکل اتصال به دیتابیس

- مطمئن شوید PostgreSQL در حال اجرا است
- بررسی کنید که اطلاعات اتصال در `.env` صحیح است
- پورت 5432 باز است
- با Docker: `docker-compose ps` برای بررسی وضعیت

### مشکل اتصال به Redis

- مطمئن شوید Redis در حال اجرا است
- بررسی کنید که `REDIS_URL` صحیح است
- با Docker: `docker-compose ps` برای بررسی وضعیت

### مشکل در فرانت‌اند

- مطمئن شوید Node.js و npm نصب شده‌اند
- `node_modules` را پاک کنید و دوباره نصب کنید: 
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

### مشکل در CLI

```bash
# بررسی نصب
which wework
wework version

# نصب مجدد
pip uninstall wework-framework
pip install wework-framework
```

## 📚 مراحل بعدی

پس از نصب موفق:

1. ✅ [راهنمای سریع](./quickstart.md) را مطالعه کنید
2. ✅ [ساختار پروژه](./project-structure.md) را بررسی کنید
3. ✅ [پیکربندی اولیه](./configuration.md) را تنظیم کنید
4. ✅ [مستندات CLI](../CLI.md) را مطالعه کنید

## 🔄 آپدیت فریمورک

برای آپدیت فریمورک در پروژه‌های موجود:

```bash
# با CLI
wework update

# یا با pip
pip install --upgrade wework-framework
```

---

**نکته**: اگر مشکلی دارید، به بخش [عیب‌یابی](#-عیب‌یابی) مراجعه کنید یا یک Issue در GitHub ایجاد کنید.
