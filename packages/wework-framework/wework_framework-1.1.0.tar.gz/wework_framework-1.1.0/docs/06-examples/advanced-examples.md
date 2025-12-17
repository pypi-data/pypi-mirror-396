# مثال‌های پیشرفته

این بخش شامل مثال‌های پیشرفته‌تر استفاده از فریمورک WeWork است.

## Real-time Updates

```python
# Backend: WebSocket
from fastapi import WebSocket

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

## File Upload

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # ذخیره فایل
    return {"filename": file.filename}
```

## Search و Filter

```python
@router.get("/search")
async def search(q: str, filters: dict = None):
    # جستجو
    pass
```

## مراحل بعدی

- [مثال‌های پایه](./basic-examples.md)
- [مثال‌های یکپارچه‌سازی](./integration-examples.md)

