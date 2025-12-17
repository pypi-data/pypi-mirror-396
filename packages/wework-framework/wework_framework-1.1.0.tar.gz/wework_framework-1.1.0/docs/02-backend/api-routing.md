# API و Routing

این سند نحوه ساخت API و Routing در فریمورک WeWork را توضیح می‌دهد.

## ساخت Router

### Router ساده

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/")
async def root():
    return {"message": "Hello"}
```

### اضافه کردن Router به App

```python
# در src/api/app.py
from src.api.example_api import router as example_router

app.include_router(example_router)
```

## HTTP Methods

### GET

```python
@router.get("/items")
async def get_items():
    return {"items": []}
```

### POST

```python
@router.post("/items")
async def create_item(item: ItemCreate):
    # ایجاد آیتم
    return {"message": "Created"}
```

### PUT/PATCH

```python
@router.patch("/items/{item_id}")
async def update_item(item_id: int, item: ItemUpdate):
    # به‌روزرسانی
    return {"message": "Updated"}
```

### DELETE

```python
@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    # حذف
    return {"message": "Deleted"}
```

## Path Parameters

```python
@router.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}
```

## Query Parameters

```python
from fastapi import Query

@router.get("/items")
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"skip": skip, "limit": limit}
```

## Request Body

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: str = None

@router.post("/items")
async def create_item(item: ItemCreate):
    return item
```

## Response Models

```python
class ItemOut(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True

@router.get("/items/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    return ItemOut(id=1, name="Test")
```

## Dependencies

```python
from fastapi import Depends
from src.api.auth_api import get_current_active_user

@router.get("/protected")
async def protected(current_user: User = Depends(get_current_active_user)):
    return {"user_id": current_user.id}
```

## Error Handling

```python
from fastapi import HTTPException

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Status Codes

```python
from fastapi import status

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    return {"message": "Created"}
```

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [احراز هویت](./authentication.md)

