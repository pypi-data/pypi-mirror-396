# راهنمای انتشار فریمورک

این راهنما نحوه انتشار فریمورک WeWork در GitHub و PyPI را توضیح می‌دهد.

## آماده‌سازی برای انتشار

### 1. به‌روزرسانی نسخه

```bash
# در setup.py و pyproject.toml
version = "1.0.1"  # نسخه جدید
```

### 2. به‌روزرسانی CHANGELOG

```markdown
## [1.0.1] - 2024-01-15

### Added
- ویژگی جدید

### Fixed
- رفع باگ
```

### 3. Commit و Push

```bash
git add .
git commit -m "Release version 1.0.1"
git push origin main
```

## انتشار در GitHub

### ایجاد Release

1. به GitHub بروید
2. Releases > New release
3. Tag version: `v1.0.1`
4. Release title: `Version 1.0.1`
5. Description: از CHANGELOG استفاده کنید
6. Publish release

### GitHub Actions

GitHub Actions به صورت خودکار:
- تست‌ها را اجرا می‌کند
- Package را می‌سازد
- در PyPI منتشر می‌کند (اگر Release ایجاد شود)

## انتشار در PyPI

### دستی

```bash
# Build
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### با GitHub Actions

با ایجاد Release در GitHub، به صورت خودکار در PyPI منتشر می‌شود.

## تنظیمات PyPI

### API Token

1. به PyPI بروید
2. Account Settings > API tokens
3. Token جدید ایجاد کنید
4. در GitHub Secrets اضافه کنید: `PYPI_API_TOKEN`

## بررسی انتشار

```bash
# نصب از PyPI
pip install wework-framework==1.0.1

# بررسی CLI
wework version
```

## نکات مهم

1. **همیشه CHANGELOG را به‌روز کنید**
2. **تست‌ها را قبل از انتشار اجرا کنید**
3. **Version را در تمام فایل‌ها به‌روز کنید**
4. **Release Notes را کامل بنویسید**

## Troubleshooting

### خطا در Build

```bash
# پاک کردن build قبلی
rm -rf dist/ build/ *.egg-info

# Build مجدد
python -m build
```

### خطا در Upload

```bash
# بررسی credentials
python -m twine check dist/*

# Upload مجدد
python -m twine upload dist/*
```

