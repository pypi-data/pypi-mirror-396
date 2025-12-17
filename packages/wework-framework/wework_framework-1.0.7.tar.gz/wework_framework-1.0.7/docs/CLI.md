# WeWork CLI

راهنمای استفاده از WeWork CLI برای ساخت و مدیریت پروژه‌ها.

> **نکته**: این فریمورک یک بستر خام و عمومی است. شما می‌توانید با استفاده از CLI، المان‌های مورد نیاز خود را برای هر نوع پروژه‌ای ایجاد کنید.

## 📦 نصب

```bash
pip install wework-framework
```

یا از GitHub:

```bash
pip install git+https://github.com/wecanco/WeWork.git
```

## 🚀 دستورات اصلی

### `wework create <project-name>`

ایجاد پروژه جدید با ساختار کامل:

```bash
wework create my-awesome-app
wework create my-awesome-app --path /path/to/projects
```

این دستور یک پروژه کامل با ساختار زیر ایجاد می‌کند:
- ✅ Backend (FastAPI) با تنظیمات کامل
- ✅ Frontend (React) با Vite
- ✅ Docker Compose برای PostgreSQL و Redis
- ✅ فایل‌های تنظیمات (.env.example)
- ✅ ساختار کامل پوشه‌ها

**مثال:**
```bash
# ایجاد پروژه جدید
wework create my-project

# رفتن به پوشه پروژه
cd my-project

# تنظیم محیط
cp .env.example .env
# ویرایش .env

# نصب وابستگی‌ها
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# راه‌اندازی دیتابیس
docker-compose up -d postgres redis

# ایجاد جداول
python -m src.db.create_tables

# راه‌اندازی بک‌اند
uvicorn src.api.app:app --reload

# در ترمینال جدید - راه‌اندازی فرانت‌اند
cd frontend
npm install
npm run dev
```

### `wework make:api <name>`

ساخت API Router جدید با CRUD کامل:

```bash
wework make:api products
wework make:api orders --prefix /api/v1/orders
```

**خروجی**: `src/api/products_api.py`

### `wework make:model <name>`

ساخت Model جدید برای دیتابیس:

```bash
wework make:model Product
wework make:model Order
```

**خروجی**: Model به `src/db/models.py` اضافه می‌شود

### `wework make:component <name>`

ساخت کامپوننت React:

```bash
wework make:component ProductList
wework make:component UserProfile --type class
```

**خروجی**: `frontend/src/components/ProductList.jsx`

### `wework make:hook <name>`

ساخت React Hook:

```bash
wework make:hook useProducts
wework make:hook useOrders
```

**خروجی**: `frontend/src/hooks/useProducts.js`

### `wework make:migration <name>`

ساخت Migration برای دیتابیس:

```bash
wework make:migration add_products_table
wework make:migration add_user_profile_fields
```

**خروجی**: `src/db/migrate_add_products_table.py`

### `wework version`

نمایش نسخه فریمورک:

```bash
wework version
```

### `wework update`

آپدیت فریمورک:

```bash
wework update
```

## 📝 مثال کامل: ساخت یک ماژول کامل

```bash
# 1. ساخت API
wework make:api products

# 2. ساخت Model
wework make:model Product

# 3. ساخت Component
wework make:component ProductList

# 4. ساخت Hook
wework make:hook useProducts

# 5. ساخت Migration
wework make:migration add_products_table
```

بعد از اجرای این دستورات:

1. ✅ API Router در `src/api/products_api.py` ایجاد می‌شود
2. ✅ Model به `src/db/models.py` اضافه می‌شود
3. ✅ Component در `frontend/src/components/ProductList.jsx` ایجاد می‌شود
4. ✅ Hook در `frontend/src/hooks/useProducts.js` ایجاد می‌شود
5. ✅ Migration در `src/db/migrate_add_products_table.py` ایجاد می‌شود

### استفاده از فایل‌های ایجاد شده

#### 1. اضافه کردن API به App

```python
# src/api/app.py
from src.api.products_api import router as products_router

app.include_router(products_router)
```

#### 2. اجرای Migration

```bash
python -m src.db.migrate_add_products_table
```

#### 3. استفاده از Component

```jsx
// frontend/src/App.jsx
import ProductList from './components/ProductList'

function App() {
  return <ProductList />
}
```

## 📁 ساختار فایل‌های تولید شده

### API Router

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

class ProductOut(BaseModel):
    id: int
    name: str
    description: str = None
    
    class Config:
        orm_mode = True

@router.get("", response_model=list[ProductOut])
async def list_products():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        return result.scalars().all()

@router.post("", response_model=ProductOut)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_active_user)
):
    async with AsyncSessionLocal() as session:
        db_product = Product(
            name=product.name,
            description=product.description
        )
        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        return db_product
```

### Model

```python
# src/db/models.py
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Component

```jsx
// frontend/src/components/ProductList.jsx
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { Card, Button } from '../ui'

export default function ProductList() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/products`)
      setProducts(res.data)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  return (
    <Card>
      <h2>محصولات</h2>
      {products.map(product => (
        <div key={product.id}>{product.name}</div>
      ))}
    </Card>
  )
}
```

### Hook

```javascript
// frontend/src/hooks/useProducts.js
import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'

export function useProducts() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const res = await axios.get(`${API_BASE_URL}/products`)
      setProducts(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { products, loading, error, refetch: fetchProducts }
}
```

## 💡 نکات مهم

1. **همه دستورات در ریشه پروژه اجرا می‌شوند**
   ```bash
   cd /path/to/your/project
   wework make:api products
   ```

2. **فایل‌های تولید شده نیاز به ویرایش دارند**
   - Model ها باید فیلدهای مورد نیاز را داشته باشند
   - API ها باید منطق کسب‌وکار را اضافه کنید
   - Component ها باید UI را کامل کنید

3. **از `wework update` برای آپدیت منظم استفاده کنید**
   ```bash
   wework update
   ```

4. **Migration ها را به ترتیب اجرا کنید**
   ```bash
   python -m src.db.migrate_add_products_table
   ```

## 🔧 پیکربندی

فایل `.wework` در ریشه پروژه (اختیاری):

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "framework_version": "1.0.0"
}
```

## ❓ عیب‌یابی

### CLI پیدا نمی‌شود

```bash
# بررسی نصب
which wework
pip show wework-framework

# نصب مجدد
pip uninstall wework-framework
pip install wework-framework
```

### خطا در ایجاد فایل

- مطمئن شوید در ریشه پروژه هستید
- بررسی کنید که دسترسی نوشتن دارید
- بررسی کنید که فایل از قبل وجود ندارد

## 📚 مراحل بعدی

- [راهنمای سریع](./01-getting-started/quickstart.md) - مثال کامل
- [معماری بک‌اند](./02-backend/architecture.md) - ساختار API
- [UI Kit](./04-ui-kit/introduction.md) - کامپوننت‌های React

---

**نکته**: برای مثال‌های بیشتر، به [مثال‌ها](./06-examples/basic-examples.md) مراجعه کنید.
