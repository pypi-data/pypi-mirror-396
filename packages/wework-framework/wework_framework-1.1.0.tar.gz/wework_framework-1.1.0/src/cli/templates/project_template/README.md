# {{PROJECT_NAME}}

پروژه جدید ساخته شده با WeWork Framework

## 🚀 راه‌اندازی سریع

### پیش‌نیازها

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+
- Docker (اختیاری)

### نصب و راه‌اندازی

```bash
# 1. نصب وابستگی‌های بک‌اند
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. تنظیم متغیرهای محیطی
cp .env.example .env
# فایل .env را ویرایش کنید

# 3. راه‌اندازی دیتابیس و Redis
docker-compose up -d postgres redis

# 4. ایجاد جداول دیتابیس
python -m src.db.create_tables

# 5. راه‌اندازی بک‌اند
uvicorn src.api.app:app --reload --port 8000

# 6. در ترمینال جدید - راه‌اندازی فرانت‌اند
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

## 📚 استفاده از CLI

```bash
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

## 📖 مستندات

برای مستندات کامل، به [WeWork Framework Documentation](https://github.com/wecanco/WeWork) مراجعه کنید.

---

ساخته شده با ❤️ با WeWork Framework

