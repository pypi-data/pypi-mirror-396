# {{PROJECT_NAME}} - E-commerce Template

پروژه فروشگاهی مدرن ساخته شده با WeWork Framework

این تمپلت شامل:
- ✅ طراحی مدرن و شیک
- ✅ Mobile-First و Responsive
- ✅ صفحه محصولات با فیلتر و جستجو
- ✅ صفحه جزئیات محصول
- ✅ سبد خرید (Shopping Cart)
- ✅ صفحه پرداخت (Checkout)
- ✅ Navigation Bar با آیکون سبد خرید
- ✅ Backend API کامل با FastAPI
- ✅ Performance بالا و بهینه

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
- **Frontend**: http://localhost:3000

## 📚 استفاده از CLI

```bash
# ساخت API Router جدید
wework make:api products

# ساخت Model جدید
wework make:model Product
```

---

ساخته شده با ❤️ با WeWork Framework

