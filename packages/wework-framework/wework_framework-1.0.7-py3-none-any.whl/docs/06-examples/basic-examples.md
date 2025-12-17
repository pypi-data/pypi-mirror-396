# مثال‌های پایه

این بخش شامل مثال‌های پایه استفاده از فریمورک WeWork است.

## مثال 1: API ساده

### Backend

```python
# src/api/example_api.py
from fastapi import APIRouter, Depends, HTTPException
from src.api.auth_api import get_current_active_user
from src.db.base import AsyncSessionLocal
from src.db.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/example", tags=["example"])

class ItemCreate(BaseModel):
    name: str
    description: str = None

class ItemOut(BaseModel):
    id: int
    name: str
    description: str = None
    
    class Config:
        orm_mode = True

@router.post("/items", response_model=ItemOut)
async def create_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_active_user)
):
    async with AsyncSessionLocal() as session:
        db_item = Item(
            name=item.name,
            description=item.description,
            user_id=current_user.id
        )
        session.add(db_item)
        await session.commit()
        await session.refresh(db_item)
        return db_item

@router.get("/items", response_model=list[ItemOut])
async def list_items(current_user: User = Depends(get_current_active_user)):
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Item).where(Item.user_id == current_user.id)
        )
        return result.scalars().all()
```

### Frontend

```jsx
// frontend/src/components/ItemList.jsx
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { Card, CardHeader, CardBody, Input, Button, Table } from '../ui'
import { useAuth } from './AuthContext'

export default function ItemList() {
  const { token } = useAuth()
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/example/items`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setItems(res.data)
    } catch (err) {
      console.error('Error fetching items:', err)
    }
  }

  const createItem = async () => {
    if (!name.trim()) return
    
    setLoading(true)
    try {
      await axios.post(
        `${API_BASE_URL}/example/items`,
        { name },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setName('')
      fetchItems()
    } catch (err) {
      console.error('Error creating item:', err)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { key: 'name', label: 'نام' },
    { key: 'description', label: 'توضیحات' }
  ]

  return (
    <Card>
      <CardHeader>
        <h2>لیست آیتم‌ها</h2>
      </CardHeader>
      <CardBody>
        <div style={{ marginBottom: '1rem' }}>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="نام آیتم"
            onKeyPress={(e) => e.key === 'Enter' && createItem()}
          />
          <Button 
            onClick={createItem} 
            loading={loading}
            style={{ marginTop: '0.5rem' }}
          >
            افزودن
          </Button>
        </div>
        <Table columns={columns} data={items} />
      </CardBody>
    </Card>
  )
}
```

## مثال 2: فرم با Validation

### Backend

```python
# src/api/form_api.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, validator
from src.api.auth_api import get_current_active_user
from src.db.models import User

router = APIRouter(prefix="/api/form", tags=["form"])

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('نام باید حداقل 2 کاراکتر باشد')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('09') or len(v) != 11:
            raise ValueError('شماره تلفن معتبر نیست')
        return v

@router.post("/contact")
async def submit_contact(
    form: ContactForm,
    current_user: User = Depends(get_current_active_user)
):
    # پردازش فرم
    return {
        "message": "فرم با موفقیت ارسال شد",
        "data": form.dict()
    }
```

### Frontend

```jsx
// frontend/src/components/ContactForm.jsx
import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { 
  Card, CardHeader, CardBody, CardActions,
  Input, Textarea, Button, FormRow, FormActions
} from '../ui'
import { useAuth } from './AuthContext'

export default function ContactForm() {
  const { token } = useAuth()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value })
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' })
    }
  }

  const validate = () => {
    const newErrors = {}
    
    if (!formData.name || formData.name.length < 2) {
      newErrors.name = 'نام باید حداقل 2 کاراکتر باشد'
    }
    
    if (!formData.email) {
      newErrors.email = 'ایمیل الزامی است'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'ایمیل معتبر نیست'
    }
    
    if (!formData.phone) {
      newErrors.phone = 'شماره تلفن الزامی است'
    } else if (!/^09\d{9}$/.test(formData.phone)) {
      newErrors.phone = 'شماره تلفن معتبر نیست'
    }
    
    if (!formData.message) {
      newErrors.message = 'پیام الزامی است'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validate()) return
    
    setLoading(true)
    try {
      await axios.post(
        `${API_BASE_URL}/form/contact`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert('فرم با موفقیت ارسال شد')
      setFormData({ name: '', email: '', phone: '', message: '' })
    } catch (err) {
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (Array.isArray(detail)) {
          const newErrors = {}
          detail.forEach(item => {
            newErrors[item.loc[1]] = item.msg
          })
          setErrors(newErrors)
        } else {
          alert(detail)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <h2>فرم تماس</h2>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardBody>
          <FormRow columns={2}>
            <Input
              label="نام"
              value={formData.name}
              onChange={handleChange('name')}
              error={errors.name}
              required
            />
            <Input
              label="ایمیل"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              error={errors.email}
              required
            />
          </FormRow>
          
          <Input
            label="شماره تلفن"
            type="tel"
            value={formData.phone}
            onChange={handleChange('phone')}
            error={errors.phone}
            required
          />
          
          <Textarea
            label="پیام"
            value={formData.message}
            onChange={handleChange('message')}
            rows={5}
            error={errors.message}
            required
          />
        </CardBody>
        
        <CardActions>
          <FormActions>
            <Button type="button" variant="secondary">
              انصراف
            </Button>
            <Button type="submit" variant="primary" loading={loading}>
              ارسال
            </Button>
          </FormActions>
        </CardActions>
      </form>
    </Card>
  )
}
```

## مثال 3: استفاده از Redis

### Backend

```python
# src/api/cache_api.py
from fastapi import APIRouter
from src.core.redis_manager import redis_manager

router = APIRouter(prefix="/api/cache", tags=["cache"])

@router.post("/set")
async def set_cache(key: str, value: str, expire: int = 3600):
    await redis_manager.set(key, value, expire=expire)
    return {"message": "Cache set successfully"}

@router.get("/get/{key}")
async def get_cache(key: str):
    value = await redis_manager.get(key)
    if value is None:
        return {"message": "Cache not found"}
    return {"key": key, "value": value}

@router.delete("/delete/{key}")
async def delete_cache(key: str):
    await redis_manager.delete(key)
    return {"message": "Cache deleted"}
```

## مثال 4: استفاده از Event Dispatcher

### Backend

```python
# src/api/event_api.py
from fastapi import APIRouter
from src.core.event_dispatcher import event_dispatcher

router = APIRouter(prefix="/api/event", tags=["event"])

# ثبت Event Handler
@event_dispatcher.on("user.created")
async def handle_user_created(event_data):
    print(f"User created: {event_data['user_id']}")
    # ارسال ایمیل، SMS و ...

@router.post("/trigger")
async def trigger_event():
    # ارسال Event
    await event_dispatcher.emit("user.created", {
        "user_id": 123,
        "email": "user@example.com"
    })
    return {"message": "Event triggered"}
```

## مثال 5: Modal با فرم

### Frontend

```jsx
// frontend/src/components/ItemModal.jsx
import React, { useState } from 'react'
import { Modal, Input, Button, FormRow, FormActions } from '../ui'

export default function ItemModal({ open, onClose, onSubmit, item }) {
  const [formData, setFormData] = useState({
    name: item?.name || '',
    description: item?.description || ''
  })
  const [errors, setErrors] = useState({})

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value })
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' })
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      setErrors({ name: 'نام الزامی است' })
      return
    }
    
    onSubmit(formData)
    onClose()
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={item ? 'ویرایش آیتم' : 'افزودن آیتم'}
      footer={
        <FormActions>
          <Button type="button" variant="secondary" onClick={onClose}>
            انصراف
          </Button>
          <Button type="submit" variant="primary" onClick={handleSubmit}>
            ذخیره
          </Button>
        </FormActions>
      }
    >
      <form onSubmit={handleSubmit}>
        <Input
          label="نام"
          value={formData.name}
          onChange={handleChange('name')}
          error={errors.name}
          required
        />
        <Input
          label="توضیحات"
          value={formData.description}
          onChange={handleChange('description')}
        />
      </form>
    </Modal>
  )
}
```

## مراحل بعدی

- [مثال‌های پیشرفته](./advanced-examples.md)
- [مثال‌های یکپارچه‌سازی](./integration-examples.md)

