# مدیریت کارها و Background Jobs

این سند نحوه مدیریت Background Jobs در فریمورک WeWork را توضیح می‌دهد.

## Background Tasks

### با FastAPI BackgroundTasks

```python
from fastapi import BackgroundTasks

@router.post("/send-email")
async def send_email(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_task, email)
    return {"message": "Email will be sent"}
```

## Scheduled Tasks

### با asyncio

```python
import asyncio

async def periodic_task():
    while True:
        # انجام کار
        await process_data()
        await asyncio.sleep(3600)  # هر ساعت

# در startup
asyncio.create_task(periodic_task())
```

## Job Queue

### با Redis

```python
from src.core.redis_manager import redis_manager

async def enqueue_job(job_type: str, data: dict):
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "type": job_type,
        "data": data,
        "status": "pending"
    }
    await redis_manager.lpush("jobs:queue", json.dumps(job))
    return job_id

async def process_jobs():
    while True:
        job_json = await redis_manager.brpop("jobs:queue", timeout=1)
        if job_json:
            job = json.loads(job_json[1])
            await execute_job(job)
```

## Task Examples

### Email Sending

```python
async def send_email_task(email: str, subject: str, body: str):
    # ارسال ایمیل
    pass

# استفاده
background_tasks.add_task(send_email_task, email, subject, body)
```

### Data Processing

```python
async def process_data_task(data_id: int):
    # پردازش داده
    pass
```

## Best Practices

1. **Error Handling**: خطاها را handle کنید
2. **Retry Logic**: برای کارهای مهم retry اضافه کنید
3. **Monitoring**: وضعیت کارها را monitor کنید
4. **Resource Management**: منابع را مدیریت کنید

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [یکپارچه‌سازی‌ها](./integrations.md)

