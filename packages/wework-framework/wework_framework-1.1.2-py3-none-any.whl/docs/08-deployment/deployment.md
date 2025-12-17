# راهنمای استقرار

این راهنما نحوه استقرار فریمورک WeWork را توضیح می‌دهد.

## Production Setup

```bash
# نصب
pip install wework-framework

# تنظیمات
export DATABASE_URL=...
export REDIS_URL=...

# اجرا
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

## مراحل بعدی

- [Docker و Containerization](./docker.md)
- [CI/CD](./cicd.md)

