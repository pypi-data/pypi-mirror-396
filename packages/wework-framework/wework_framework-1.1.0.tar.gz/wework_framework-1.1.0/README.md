# WeWork Framework

فریمورک خام و ماژولار برای ساخت اپلیکیشن‌های وب مدرن با Python (FastAPI) و React.

این فریمورک یک بستر خام و عمومی است که به شما امکان ساخت هر نوع اپلیکیشنی را می‌دهد. با استفاده از CLI می‌توانید به سرعت المان‌های مختلف (API، Model، Component، Hook و ...) را ایجاد کنید.

[![PyPI version](https://badge.fury.io/py/wework-framework.svg)](https://badge.fury.io/py/wework-framework)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 راه‌اندازی سریع

### پیش‌نیازها

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+
- Docker (اختیاری)

### ایجاد پروژه جدید

```bash
# نصب فریمورک
pip install wework-framework

# ایجاد پروژه جدید (با انتخاب تمپلت از منوی تعاملی)
wework create my-awesome-app

# یا مستقیماً با مشخص کردن تمپلت
wework create my-awesome-app --template corporate
wework create my-awesome-app --template ecommerce
wework create my-awesome-app --template admin
wework create my-awesome-app --template messaging

# رفتن به پوشه پروژه
cd my-awesome-app

# تنظیم محیط
cp .env.example .env
# فایل .env را ویرایش کنید

# نصب وابستگی‌های بک‌اند
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# راه‌اندازی دیتابیس و Redis
docker-compose up -d postgres redis

# ایجاد جداول دیتابیس
python -m src.db.create_tables

# راه‌اندازی بک‌اند
uvicorn src.api.app:app --reload --port 8000

# در ترمینال جدید - راه‌اندازی فرانت‌اند
cd frontend
npm install
npm run dev
```

### نصب و راه‌اندازی (روش قدیمی - کلون از GitHub)

```bash
# 1. کلون کردن پروژه
git clone https://github.com/wecanco/WeWork.git
cd WeWork

# 2. نصب وابستگی‌های بک‌اند
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. تنظیم متغیرهای محیطی
cp .env.example .env
# فایل .env را ویرایش کنید

# 4. راه‌اندازی دیتابیس و Redis
docker-compose up -d postgres redis

# 5. ایجاد جداول دیتابیس
python -m src.db.create_tables

# 6. راه‌اندازی بک‌اند
uvicorn src.api.app:app --reload --port 8000

# 7. در ترمینال جدید - راه‌اندازی فرانت‌اند
cd frontend
npm install
npm run dev
```

✅ **تمام!** حالا می‌توانید به آدرس‌های زیر دسترسی داشته باشید:
- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

### راه‌اندازی با Docker (ساده‌تر)

```bash
# راه‌اندازی همه سرویس‌ها
docker-compose up -d

# ایجاد جداول دیتابیس
docker-compose exec api python -m src.db.create_tables
```

## 📚 ویژگی‌ها

### Backend
- ✅ **FastAPI**: API مدرن و سریع با مستندات خودکار
- ✅ **Authentication**: سیستم احراز هویت کامل با JWT و OTP
- ✅ **Database**: PostgreSQL با SQLAlchemy Async
- ✅ **Redis**: Cache و Pub/Sub
- ✅ **Event System**: سیستم رویداد یکپارچه
- ✅ **CLI Tool**: ابزار خط فرمان برای ساخت سریع المان‌ها

### Frontend
- ✅ **React 19**: آخرین نسخه React
- ✅ **UI Kit**: مجموعه کامل کامپوننت‌های قابل استفاده مجدد
- ✅ **Responsive Design**: طراحی واکنش‌گرا برای تمام دستگاه‌ها
- ✅ **RTL Support**: پشتیبانی کامل از راست به چپ
- ✅ **Dark Mode**: تم دارک آماده
- ✅ **PWA**: Progressive Web App

### ماژول‌های پایه
- ✅ **Authentication Module**: احراز هویت کامل
- ✅ **User Management**: مدیریت کاربران
- ✅ **Billing Module**: پرداخت و اشتراک
- ✅ **Notifications**: اعلان‌رسانی (SMS, Web Push)
- ✅ **Admin Panel**: پنل مدیریت کامل

## 🛠️ استفاده از CLI

### تمپلت‌های آماده

WeWork Framework شامل 5 تمپلت آماده است که می‌توانید از آن‌ها استفاده کنید:

1. **Basic** - تمپلت پایه و ساده برای شروع
2. **Corporate** - وب‌سایت شرکتی با صفحات خدمات، درباره ما و تماس
3. **E-commerce** - فروشگاه آنلاین کامل با سبد خرید و پرداخت
4. **Admin Panel** - پنل مدیریتی حرفه‌ای با داشبورد و جداول
5. **Messaging** - سامانه ارسال پیام برای پیام‌رسان‌های ایرانی با مدیریت اکانت و ارسال توزیع شده

```bash
# ایجاد پروژه با انتخاب تمپلت از منوی تعاملی
wework create my-project

# یا مستقیماً با مشخص کردن تمپلت
wework create my-corporate-site --template corporate
wework create my-online-store --template ecommerce
wework create my-admin-panel --template admin
wework create my-messaging-app --template messaging
```

### دستورات اصلی

```bash
# ایجاد پروژه جدید
wework create my-project

# ساخت API Router جدید
wework make:api products

# ساخت Model جدید
wework make:model Product

# ساخت Component جدید
wework make:component ProductList

# ساخت Hook جدید
wework make:hook useProducts

# ساخت Migration جدید
wework make:migration add_products_table
```

### مثال: ایجاد یک API کامل

```bash
# 1. ساخت API
wework make:api products

# 2. ساخت Model
wework make:model Product

# 3. ساخت Component
wework make:component ProductList

# 4. ساخت Hook
wework make:hook useProducts

# 5. ساخت Migration
wework make:migration add_products_table
```

بعد از اجرای دستورات بالا، فایل‌های زیر ایجاد می‌شوند:
- `src/api/products_api.py` - API Router با CRUD کامل
- `src/db/models.py` - Model جدید اضافه می‌شود
- `frontend/src/components/ProductList.jsx` - Component React
- `frontend/src/hooks/useProducts.js` - Hook برای fetch داده
- `src/db/migrate_add_products_table.py` - Migration

### استفاده از API ایجاد شده

```python
# فایل src/api/products_api.py به صورت خودکار ایجاد می‌شود
# فقط کافی است آن را به app.py اضافه کنید:

from src.api.products_api import router as products_router
app.include_router(products_router)
```

## 📖 مستندات

مستندات کامل در پوشه `docs/` قرار دارد:

- **[راهنمای نصب](docs/01-getting-started/installation.md)** - نصب و راه‌اندازی کامل
- **[راهنمای سریع](docs/01-getting-started/quickstart.md)** - شروع سریع در 10 دقیقه
- **[CLI Commands](docs/CLI.md)** - راهنمای کامل CLI
- **[معماری بک‌اند](docs/02-backend/architecture.md)** - معماری و ساختار
- **[UI Kit](docs/04-ui-kit/introduction.md)** - کامپوننت‌های React
- **[مثال‌ها](docs/06-examples/basic-examples.md)** - مثال‌های کاربردی

برای فهرست کامل، به [README مستندات](docs/README.md) مراجعه کنید.

## 🏗️ ساختار پروژه

```
WeWork/
├── docs/              # مستندات کامل
├── frontend/         # فرانت‌اند React
│   ├── src/
│   │   ├── components/  # کامپوننت‌های React
│   │   ├── hooks/       # React Hooks
│   │   └── ui/          # UI Kit
├── src/              # بک‌اند Python
│   ├── api/          # API Endpoints
│   ├── cli/          # CLI Tool
│   ├── config/       # تنظیمات
│   ├── db/           # دیتابیس
│   ├── core/         # ماژول‌های اصلی
│   └── integrations/ # یکپارچه‌سازی‌ها
├── examples/         # مثال‌های استفاده
└── services/         # Docker Services
```

## 💡 مثال سریع

### ایجاد یک API ساده

```python
# src/api/my_api.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/my", tags=["my"])

@router.get("/hello")
async def hello():
    return {"message": "Hello from WeWork!"}
```

### استفاده از UI Kit

```jsx
import { Button, Card } from '../ui'

function MyComponent() {
  return (
    <Card>
      <h3>عنوان</h3>
      <Button variant="primary">کلیک کنید</Button>
    </Card>
  )
}
```

## 🔧 تنظیمات اولیه

فایل `.env` را در ریشه پروژه ایجاد کنید:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=wework

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis
REDIS_URL=redis://localhost:6379/0

# Frontend
FRONTEND_BASE_URL=http://localhost:5173
```

## 📦 نصب از PyPI

```bash
pip install wework-framework
```

## 🤝 مشارکت

برای مشارکت در توسعه:

1. Fork کنید
2. Branch جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
3. Commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

برای راهنمای توسعه، به [CONTRIBUTING.md](CONTRIBUTING.md) مراجعه کنید.

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات، به [LICENSE](LICENSE) مراجعه کنید.

## 📞 پشتیبانی

برای سوالات و پشتیبانی:
- Issues در GitHub
- مستندات کامل در `docs/`

## 📝 تغییرات

برای مشاهده تغییرات و به‌روزرسانی‌ها، به [CHANGELOG.md](CHANGELOG.md) مراجعه کنید.

---

ساخته شده با ❤️ برای توسعه‌دهندگان
