# راهنمای سریع

این راهنما به شما کمک می‌کند تا در کمتر از 10 دقیقه اولین اپلیکیشن خود را با فریمورک WeWork بسازید.

> **💡 نکته**: اگر می‌خواهید سریع‌تر شروع کنید، می‌توانید از [تمپلت‌های آماده](./templates.md) استفاده کنید:
> ```bash
> wework create my-project --template corporate
> wework create my-project --template ecommerce
> wework create my-project --template admin
> wework create my-project --template messaging
> ```

## 🎯 هدف

در این راهنما، یک API ساده برای مدیریت محصولات (Products) می‌سازیم که شامل:
- ایجاد محصول
- لیست محصولات
- مشاهده یک محصول
- به‌روزرسانی محصول
- حذف محصول

## 📝 گام 1: ساخت API

با استفاده از CLI، یک API Router جدید ایجاد کنید:

```bash
wework make:api products
```

این دستور فایل `src/api/products_api.py` را ایجاد می‌کند.

## 📝 گام 2: ساخت Model

یک Model برای Product ایجاد کنید:

```bash
wework make:model Product
```

این دستور Model را به `src/db/models.py` اضافه می‌کند.

## 📝 گام 3: اضافه کردن API به App

فایل `src/api/app.py` را باز کنید و Router جدید را اضافه کنید:

```python
from src.api.products_api import router as products_router

# بعد از سایر router ها
app.include_router(products_router)
```

## 📝 گام 4: ایجاد Migration

Migration برای ایجاد جدول products:

```bash
wework make:migration add_products_table
```

سپس Migration را اجرا کنید:

```bash
python -m src.db.migrate_add_products_table
```

یا اگر از Docker استفاده می‌کنید:

```bash
docker-compose exec api python -m src.db.migrate_add_products_table
```

## 📝 گام 5: تست API

بک‌اند را راه‌اندازی کنید (اگر در حال اجرا نیست):

```bash
uvicorn src.api.app:app --reload --port 8000
```

حالا به آدرس http://localhost:8000/docs بروید و API جدید را تست کنید.

## 🎨 گام 6: ساخت Component (اختیاری)

برای فرانت‌اند، یک Component ایجاد کنید:

```bash
wework make:component ProductList
```

این Component را در `App.jsx` یا هر Route دیگری استفاده کنید.

## 📚 مثال کامل

### Backend API

```python
# src/api/products_api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from src.api.auth_api import get_current_active_user
from src.db.base import AsyncSessionLocal
from src.db.models import User, Product
from pydantic import BaseModel

router = APIRouter(prefix="/api/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    description: str = None
    price: float

class ProductOut(BaseModel):
    id: int
    name: str
    description: str = None
    price: float
    
    class Config:
        orm_mode = True

@router.post("", response_model=ProductOut)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_active_user)
):
    async with AsyncSessionLocal() as session:
        db_product = Product(
            name=product.name,
            description=product.description,
            price=product.price
        )
        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        return db_product

@router.get("", response_model=list[ProductOut])
async def list_products():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        return result.scalars().all()

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int):
    async with AsyncSessionLocal() as session:
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
```

### Frontend Component

```jsx
// frontend/src/components/ProductList.jsx
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { Card, Button, Input } from '../ui'

export default function ProductList() {
  const [products, setProducts] = useState([])
  const [name, setName] = useState('')
  const [price, setPrice] = useState('')

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/products`)
      setProducts(res.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    }
  }

  const createProduct = async () => {
    try {
      await axios.post(`${API_BASE_URL}/products`, {
        name,
        price: parseFloat(price)
      })
      setName('')
      setPrice('')
      fetchProducts()
    } catch (error) {
      console.error('Error creating product:', error)
    }
  }

  return (
    <div>
      <Card>
        <h2>افزودن محصول</h2>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="نام محصول"
        />
        <Input
          type="number"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="قیمت"
        />
        <Button onClick={createProduct}>افزودن</Button>
      </Card>

      <div>
        <h2>لیست محصولات</h2>
        {products.map(product => (
          <Card key={product.id}>
            <h3>{product.name}</h3>
            <p>{product.description}</p>
            <p>قیمت: {product.price} تومان</p>
          </Card>
        ))}
      </div>
    </div>
  )
}
```

## 🎉 تبریک!

شما اولین API و Component خود را با WeWork Framework ساختید!

## 📚 مراحل بعدی

- [معماری بک‌اند](../02-backend/architecture.md) را مطالعه کنید
- [UI Kit](../04-ui-kit/introduction.md) را بررسی کنید
- [مثال‌های پیشرفته](../06-examples/advanced-examples.md) را ببینید
- [مستندات CLI](../CLI.md) را مطالعه کنید

---

**نکته**: برای مثال‌های بیشتر، به پوشه `examples/` مراجعه کنید.
