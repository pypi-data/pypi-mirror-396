# Docker و Containerization

این سند نحوه استفاده از Docker در فریمورک WeWork را توضیح می‌دهد.

## Docker Compose

```bash
docker-compose up -d
```

## Dockerfile

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0"]
```

## مراحل بعدی

- [راهنمای استقرار](./deployment.md)
- [CI/CD](./cicd.md)

