# مستندات فریمورک WeWork

به مستندات کامل فریمورک WeWork خوش آمدید. این فریمورک یک پلتفرم خام و ماژولار برای ساخت اپلیکیشن‌های وب مدرن است.

> **نکته**: این فریمورک خام است و شما می‌توانید با استفاده از CLI، المان‌های مورد نیاز خود را برای هر نوع پروژه‌ای ایجاد کنید.

## 🚀 شروع سریع

برای شروع سریع، به ترتیب زیر عمل کنید:

1. **[نصب و راه‌اندازی](./01-getting-started/installation.md)** - راه‌اندازی در 5 دقیقه
2. **[تمپلت‌های آماده](./01-getting-started/templates.md)** - استفاده از تمپلت‌های آماده (پیشنهادی)
3. **[راهنمای سریع](./01-getting-started/quickstart.md)** - ساخت اولین API در 10 دقیقه
4. **[ساختار پروژه](./01-getting-started/project-structure.md)** - آشنایی با ساختار
5. **[CLI Commands](../CLI.md)** - یادگیری دستورات CLI

> **💡 نکته**: برای شروع سریع‌تر، می‌توانید از تمپلت‌های آماده استفاده کنید:
> - `corporate` - وب‌سایت شرکتی
> - `ecommerce` - فروشگاه آنلاین
> - `admin` - پنل مدیریتی
> - `messaging` - سامانه ارسال پیام

## 📚 فهرست مطالب

### 1. راهنمای شروع
- [نصب و راه‌اندازی](./01-getting-started/installation.md) - راه‌اندازی کامل
- [راهنمای سریع](./01-getting-started/quickstart.md) - شروع سریع در 10 دقیقه
- [تمپلت‌های آماده](./01-getting-started/templates.md) - استفاده از تمپلت‌ها
- [ساختار پروژه](./01-getting-started/project-structure.md) - ساختار فایل‌ها
- [پیکربندی اولیه](./01-getting-started/configuration.md) - تنظیمات

### 2. بک‌اند (Backend)
- [معماری بک‌اند](./02-backend/architecture.md) - معماری و ساختار
- [احراز هویت](./02-backend/authentication.md) - JWT و OTP
- [مدیریت دیتابیس](./02-backend/database.md) - PostgreSQL و SQLAlchemy
- [API و Routing](./02-backend/api-routing.md) - ساخت API
- [Redis و Cache](./02-backend/redis-cache.md) - مدیریت Cache
- [رویدادها](./02-backend/events.md) - Event System
- [Background Jobs](./02-backend/tasks-jobs.md) - کارهای پس‌زمینه
- [یکپارچه‌سازی‌ها](./02-backend/integrations.md) - SMS, Web Push و ...

### 3. فرانت‌اند (Frontend)
- [معماری فرانت‌اند](./03-frontend/architecture.md) - ساختار React
- [UI Kit](./03-frontend/ui-kit.md) - کامپوننت‌های آماده
- [State Management](./03-frontend/state-management.md) - مدیریت State
- [Routing](./03-frontend/routing.md) - Navigation
- [Hooks و Utilities](./03-frontend/hooks-utils.md) - Hooks مفید
- [استایل‌دهی](./03-frontend/styling-theme.md) - Theme و Styling

### 4. UI Kit
- [معرفی UI Kit](./04-ui-kit/introduction.md) - شروع با UI Kit
- [کامپوننت‌های پایه](./04-ui-kit/basic-components.md) - Button, Card, Badge
- [کامپوننت‌های فرم](./04-ui-kit/form-components.md) - Input, Select, Form
- [کامپوننت‌های پیشرفته](./04-ui-kit/advanced-components.md) - Modal, Table
- [Theme](./04-ui-kit/theme-customization.md) - سفارشی‌سازی Theme

### 5. ماژول‌ها
- [احراز هویت](./05-modules/authentication.md) - Authentication Module
- [مدیریت کاربران](./05-modules/user-management.md) - User Management
- [پرداخت](./05-modules/billing.md) - Billing و Subscription
- [اعلان‌رسانی](./05-modules/notifications.md) - Notifications
- [مدیریت فایل](./05-modules/file-management.md) - File Management

### 6. مثال‌ها
- [مثال‌های پایه](./06-examples/basic-examples.md) - مثال‌های ساده
- [مثال‌های پیشرفته](./06-examples/advanced-examples.md) - مثال‌های پیچیده
- [یکپارچه‌سازی](./06-examples/integration-examples.md) - Integration Examples

### 7. توسعه
- [راهنمای توسعه](./07-development/development-guide.md) - Best Practices
- [تست‌نویسی](./07-development/testing.md) - Testing
- [Performance](./07-development/performance.md) - بهینه‌سازی
- [Debugging](./07-development/debugging.md) - عیب‌یابی

### 8. استقرار
- [راهنمای استقرار](./08-deployment/deployment.md) - Deployment Guide
- [Docker](./08-deployment/docker.md) - Containerization
- [CI/CD](./08-deployment/cicd.md) - Continuous Integration

### 9. API Reference
- [مرجع API](./09-api-reference/overview.md) - API Overview
- [Authentication API](./09-api-reference/authentication.md) - Auth Endpoints
- [User Management API](./09-api-reference/user-management.md) - User Endpoints
- [Billing API](./09-api-reference/billing.md) - Billing Endpoints

## 🛠️ CLI Commands

برای راهنمای کامل CLI، به [CLI.md](./CLI.md) مراجعه کنید.

### ایجاد پروژه از تمپلت

```bash
wework create my-project                    # انتخاب از منوی تعاملی
wework create my-project --template corporate
wework create my-project --template ecommerce
wework create my-project --template admin
wework create my-project --template messaging
```

### دستورات اصلی

```bash
wework make:api <name>      # ساخت API Router
wework make:model <name>    # ساخت Model
wework make:component <name> # ساخت Component
wework make:hook <name>     # ساخت Hook
wework make:migration <name> # ساخت Migration
```

## 📖 مثال سریع

### ساخت API

```bash
wework make:api products
```

### ساخت Model

```bash
wework make:model Product
```

### ساخت Component

```bash
wework make:component ProductList
```

## 🤝 پشتیبانی

برای سوالات و پشتیبانی:
- Issues در GitHub
- مستندات کامل در این پوشه

## 📝 تغییرات

برای مشاهده تغییرات، به [CHANGELOG.md](../CHANGELOG.md) مراجعه کنید.

---

**نکته**: اگر تازه شروع کرده‌اید، حتماً [راهنمای نصب](./01-getting-started/installation.md) و [راهنمای سریع](./01-getting-started/quickstart.md) را مطالعه کنید.
