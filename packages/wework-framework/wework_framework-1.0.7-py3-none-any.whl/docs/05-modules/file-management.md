# ماژول مدیریت فایل

این ماژول مدیریت آپلود و دانلود فایل‌ها را فراهم می‌کند.

## استفاده

```python
from fastapi import UploadFile

@router.post("/upload")
async def upload_file(file: UploadFile):
    # آپلود فایل
    pass
```

## مراحل بعدی

- [API و Routing](../02-backend/api-routing.md)

