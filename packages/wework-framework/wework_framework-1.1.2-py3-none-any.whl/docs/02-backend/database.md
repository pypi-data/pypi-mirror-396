# مدیریت دیتابیس

این سند نحوه کار با دیتابیس در فریمورک WeWork را توضیح می‌دهد.

## اتصال به دیتابیس

### تنظیمات

```python
# در .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

### Base و Session

```python
from src.db.base import Base, AsyncSessionLocal, engine

# استفاده از Session
async with AsyncSessionLocal() as session:
    # کار با دیتابیس
    pass
```

## Models

### تعریف Model

```python
from src.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Relationships

```python
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # ...

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="items")
```

## CRUD Operations

### Create

```python
async with AsyncSessionLocal() as session:
    item = Item(name="Test", description="Description")
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
```

### Read

```python
from sqlalchemy import select

# Get by ID
async with AsyncSessionLocal() as session:
    item = await session.get(Item, item_id)

# Query
async with AsyncSessionLocal() as session:
    result = await session.execute(select(Item).where(Item.name == "Test"))
    items = result.scalars().all()
```

### Update

```python
async with AsyncSessionLocal() as session:
    item = await session.get(Item, item_id)
    if item:
        item.name = "New Name"
        session.add(item)
        await session.commit()
        await session.refresh(item)
```

### Delete

```python
async with AsyncSessionLocal() as session:
    item = await session.get(Item, item_id)
    if item:
        await session.delete(item)
        await session.commit()
```

## Migrations

### ایجاد Migration

```python
# src/db/migrate_add_items.py
from src.db.base import Base, engine

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### اجرای Migration

```bash
python -m src.db.migrate_add_items
```

## Repository Pattern

### استفاده از Repository

```python
from src.db.repos import BaseRepository

class ItemRepository(BaseRepository):
    model = Item
    
    async def get_by_name(self, name: str):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(self.model).where(self.model.name == name)
            )
            return result.scalar_one_or_none()
```

## Transactions

```python
async with AsyncSessionLocal() as session:
    async with session.begin():
        item1 = Item(name="Item 1")
        item2 = Item(name="Item 2")
        session.add(item1)
        session.add(item2)
        # اگر خطایی رخ دهد، هر دو rollback می‌شوند
```

## Best Practices

1. **همیشه از async/await استفاده کنید**
2. **Session را به درستی ببندید**
3. **از Transactions برای عملیات چندگانه استفاده کنید**
4. **Index ها را برای فیلدهای پرجستجو اضافه کنید**

## مراحل بعدی

- [معماری بک‌اند](./architecture.md)
- [API و Routing](./api-routing.md)

