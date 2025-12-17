# نصب و استفاده از فریمورک WeWork

این راهنما نحوه نصب و استفاده از فریمورک WeWork در پروژه‌های جدید را توضیح می‌دهد.

## نصب از PyPI

```bash
pip install wework-framework
```

## نصب از GitHub

```bash
pip install git+https://github.com/wecanco/WeWork.git
```

## ایجاد پروژه جدید

### روش 1: استفاده از CLI

```bash
# نصب CLI
pip install wework-framework

# ایجاد پروژه
wework init --name my-project
cd my-project
```

### روش 2: نصب دستی

```bash
# ایجاد پروژه
mkdir my-project
cd my-project

# نصب فریمورک
pip install wework-framework

# ایجاد ساختار اولیه
wework init --name my-project --path .
```

## استفاده در پروژه موجود

### نصب

```bash
pip install wework-framework
```

### استفاده از ماژول‌ها

```python
# استفاده از Authentication
from src.api.auth_api import get_current_active_user, get_password_hash

# استفاده از Database
from src.db.base import AsyncSessionLocal
from src.db.models import User

# استفاده از Core Modules
from src.core.redis_manager import redis_manager
from src.core.event_dispatcher import event_dispatcher
```

## آپدیت فریمورک

```bash
# آپدیت به آخرین نسخه
wework update

# یا با pip
pip install --upgrade wework-framework
```

## بررسی نسخه

```bash
wework version
```

## استفاده از CLI

```bash
# ساخت API
wework make:api products

# ساخت Model
wework make:model Product

# ساخت Component
wework make:component ProductList

# ساخت Hook
wework make:hook useProducts

# ساخت Migration
wework make:migration add_products_table
```

## پیکربندی

فایل `.wework` در ریشه پروژه:

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "framework_version": "1.0.0"
}
```

## مثال کامل

```bash
# 1. نصب
pip install wework-framework

# 2. ایجاد پروژه
wework init --name my-app
cd my-app

# 3. ساخت API
wework make:api products

# 4. ساخت Model
wework make:model Product

# 5. ساخت Component
wework make:component ProductList

# 6. اجرا
uvicorn src.api.app:app --reload
```

## نکات مهم

1. **همیشه از آخرین نسخه استفاده کنید**: `wework update`
2. **فایل .wework را commit کنید**: برای ردیابی نسخه فریمورک
3. **از CLI استفاده کنید**: برای ساخت سریع‌تر بخش‌ها
4. **مستندات را مطالعه کنید**: در پوشه `docs/`

## عیب‌یابی

### مشکل در نصب

```bash
# نصب مجدد
pip uninstall wework-framework
pip install wework-framework
```

### مشکل در CLI

```bash
# بررسی نصب
which wework
wework version
```

### مشکل در آپدیت

```bash
# آپدیت دستی
pip install --upgrade --force-reinstall wework-framework
```

## پشتیبانی

- Issues: https://github.com/wecanco/WeWork/issues
- Documentation: https://github.com/wecanco/WeWork/docs

