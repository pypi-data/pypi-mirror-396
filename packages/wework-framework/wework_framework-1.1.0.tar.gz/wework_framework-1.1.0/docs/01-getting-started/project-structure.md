# ساختار پروژه

این سند ساختار کامل پروژه فریمورک WeWork را توضیح می‌دهد.

## 📁 ساختار کلی

```
WeWork/
├── docs/                    # مستندات کامل فریمورک
│   ├── 01-getting-started/  # راهنمای شروع
│   ├── 02-backend/          # مستندات بک‌اند
│   ├── 03-frontend/         # مستندات فرانت‌اند
│   ├── 04-ui-kit/           # مستندات UI Kit
│   ├── 05-modules/          # مستندات ماژول‌ها
│   ├── 06-examples/         # مثال‌ها و نمونه‌ها
│   ├── 07-development/      # راهنمای توسعه
│   ├── 08-deployment/        # راهنمای استقرار
│   └── 09-api-reference/    # مرجع API
│
├── frontend/                # فرانت‌اند React
│   ├── src/
│   │   ├── components/      # کامپوننت‌های اپلیکیشن
│   │   │   ├── HomePage.jsx
│   │   │   ├── LandingPage.jsx
│   │   │   ├── DashboardLayout.jsx
│   │   │   └── ...
│   │   ├── ui/              # UI Kit (کامپوننت‌های قابل استفاده مجدد)
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   └── ...
│   │   ├── hooks/           # Custom Hooks
│   │   │   ├── useAppVersion.js
│   │   │   ├── useHistory.js
│   │   │   └── ...
│   │   ├── utils/           # توابع کمکی
│   │   ├── config.js        # تنظیمات فرانت‌اند
│   │   ├── App.jsx          # کامپوننت اصلی
│   │   └── main.jsx         # Entry Point
│   ├── public/              # فایل‌های استاتیک
│   ├── package.json
│   └── vite.config.js       # تنظیمات Vite
│
├── src/                     # بک‌اند Python
│   ├── api/                 # API Endpoints
│   │   ├── app.py           # FastAPI Application
│   │   ├── auth_api.py      # Authentication API
│   │   ├── admin_api.py     # Admin API
│   │   ├── billing_api.py   # Billing API
│   │   ├── notifications_api.py  # Notifications API
│   │   └── ...              # API های شما (با CLI ایجاد می‌شوند)
│   │
│   ├── cli/                 # CLI Tool
│   │   ├── main.py          # Entry Point CLI
│   │   └── commands.py      # دستورات CLI
│   │
│   ├── config/              # تنظیمات
│   │   ├── settings.py      # تنظیمات اصلی
│   │   └── loader.py        # Config Loader
│   │
│   ├── db/                  # دیتابیس
│   │   ├── base.py          # Base و Session
│   │   ├── models.py        # SQLAlchemy Models
│   │   ├── repos.py         # Repository Pattern
│   │   ├── create_tables.py # ایجاد جداول
│   │   └── migrate_*.py     # Migration Scripts
│   │
│   ├── core/                # ماژول‌های اصلی
│   │   ├── redis_manager.py # Redis Manager
│   │   ├── event_dispatcher.py  # Event System
│   │   └── concurrency_manager.py  # Concurrency Control
│   │
│   ├── integrations/        # یکپارچه‌سازی‌ها
│   │   ├── webpush.py       # Web Push Notifications
│   │   └── wecan_sms.py     # SMS Integration
│   │
│   ├── utils/               # توابع کمکی
│   │   └── logging.py       # Logging Configuration
│   │
│   └── init_db.py           # Database Initialization
│
├── services/                # Docker Services
│   ├── postgres/            # PostgreSQL Configuration
│   └── redis/               # Redis Configuration
│
├── examples/                # مثال‌های استفاده
│   └── basic/               # مثال‌های پایه
│
├── .env                     # متغیرهای محیطی (ایجاد کنید)
├── .env.example             # نمونه فایل .env
├── docker-compose.yml       # Docker Compose Configuration
├── Dockerfile               # Dockerfile برای Backend
├── requirements.txt         # وابستگی‌های Python
├── README.md                # README اصلی
└── QUICK_START.md           # راهنمای سریع
```

## 📂 توضیحات پوشه‌ها

### `frontend/src/components/`

کامپوننت‌های اصلی اپلیکیشن:
- `HomePage.jsx` - صفحه اصلی داشبورد
- `LandingPage.jsx` - صفحه اصلی عمومی
- `DashboardLayout.jsx` - Layout داشبورد
- `AuthContext.jsx` - Context احراز هویت
- و کامپوننت‌های دیگر...

### `frontend/src/ui/`

UI Kit - کامپوننت‌های قابل استفاده مجدد:
- `Button.jsx` - دکمه
- `Card.jsx` - کارت
- `Input.jsx` - فیلد ورودی
- `Modal.jsx` - مودیال
- `Table.jsx` - جدول
- و کامپوننت‌های دیگر...

### `src/api/`

API Endpoints:
- `app.py` - FastAPI Application اصلی
- `auth_api.py` - احراز هویت (Login, Register, OTP)
- `admin_api.py` - پنل ادمین
- `billing_api.py` - پرداخت و اشتراک
- `notifications_api.py` - اعلان‌رسانی
- و API های شما (با `wework make:api` ایجاد می‌شوند)

### `src/db/`

مدیریت دیتابیس:
- `models.py` - SQLAlchemy Models
- `repos.py` - Repository Pattern
- `base.py` - Base و Session
- `create_tables.py` - ایجاد جداول
- `migrate_*.py` - Migration Scripts

### `src/core/`

ماژول‌های اصلی:
- `redis_manager.py` - مدیریت Redis
- `event_dispatcher.py` - سیستم رویداد
- `concurrency_manager.py` - کنترل همزمانی

### `src/cli/`

CLI Tool:
- `main.py` - Entry Point
- `commands.py` - دستورات CLI

## 🔧 فایل‌های مهم

### `.env`

متغیرهای محیطی (ایجاد کنید از `.env.example`):
```env
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=wework
JWT_SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379/0
```

### `docker-compose.yml`

پیکربندی Docker Compose برای راه‌اندازی سرویس‌ها.

### `requirements.txt`

وابستگی‌های Python.

## 📝 ایجاد المان‌های جدید

با استفاده از CLI می‌توانید المان‌های جدید ایجاد کنید:

```bash
# API
wework make:api products

# Model
wework make:model Product

# Component
wework make:component ProductList

# Hook
wework make:hook useProducts

# Migration
wework make:migration add_products_table
```

## 🎯 ساختار پیشنهادی برای پروژه‌های جدید

```
my-project/
├── src/
│   ├── api/
│   │   ├── app.py
│   │   ├── products_api.py    # API شما
│   │   └── orders_api.py      # API شما
│   ├── db/
│   │   ├── models.py          # Models شما
│   │   └── migrate_*.py       # Migrations شما
│   └── ...
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ProductList.jsx  # Component شما
│       │   └── OrderForm.jsx    # Component شما
│       └── hooks/
│           ├── useProducts.js   # Hook شما
│           └── useOrders.js     # Hook شما
└── ...
```

## 📚 مراحل بعدی

- [راهنمای سریع](./quickstart.md) - ساخت اولین API
- [CLI Commands](../CLI.md) - یادگیری CLI
- [معماری بک‌اند](../02-backend/architecture.md) - ساختار بک‌اند

---

**نکته**: ساختار پروژه ماژولار است و می‌توانید المان‌های جدید را به راحتی اضافه کنید.
