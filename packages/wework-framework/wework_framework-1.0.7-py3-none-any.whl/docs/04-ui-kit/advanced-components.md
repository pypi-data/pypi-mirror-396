# کامپوننت‌های پیشرفته

این بخش شامل کامپوننت‌های پیشرفته UI Kit است که برای ساخت رابط‌های کاربری پیچیده‌تر استفاده می‌شوند.

## Modal

کامپوننت مودیال برای نمایش دیالوگ‌ها و پنجره‌های محاوره‌ای.

### استفاده پایه

```jsx
import { Modal, Button } from '../ui'
import { useState } from 'react'

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <>
      <Button onClick={() => setIsOpen(true)}>باز کردن مودیال</Button>
      <Modal
        open={isOpen}
        onClose={() => setIsOpen(false)}
        title="عنوان مودیال"
      >
        <p>محتوای مودیال</p>
      </Modal>
    </>
  )
}
```

### Sizes

```jsx
<Modal size="sm" title="کوچک">محتوا</Modal>
<Modal size="md" title="متوسط">محتوا</Modal>
<Modal size="lg" title="بزرگ">محتوا</Modal>
<Modal size="xl" title="خیلی بزرگ">محتوا</Modal>
<Modal size="full" title="تمام صفحه">محتوا</Modal>
```

### با Footer

```jsx
<Modal
  open={isOpen}
  onClose={() => setIsOpen(false)}
  title="تایید حذف"
  footer={
    <>
      <Button variant="secondary" onClick={() => setIsOpen(false)}>
        انصراف
      </Button>
      <Button variant="danger" onClick={handleDelete}>
        حذف
      </Button>
    </>
  }
>
  آیا مطمئن هستید که می‌خواهید این آیتم را حذف کنید؟
</Modal>
```

### بدون بستن با Backdrop

```jsx
<Modal
  open={isOpen}
  onClose={() => setIsOpen(false)}
  title="مودیال اجباری"
  closeOnBackdrop={false}
>
  این مودیال فقط با دکمه X بسته می‌شود
</Modal>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | `false` | نمایش/مخفی کردن مودیال |
| `onClose` | `function` | - | Handler بستن |
| `title` | `string` | - | عنوان مودیال |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| 'full'` | `'md'` | اندازه مودیال |
| `closeOnBackdrop` | `boolean` | `true` | بستن با کلیک روی backdrop |
| `footer` | `ReactNode` | - | محتوای footer |
| `className` | `string` | `''` | کلاس‌های اضافی |
| `children` | `ReactNode` | - | محتوای مودیال |

### مثال‌های پیشرفته

```jsx
// مودیال فرم
function FormModal({ open, onClose, onSubmit }) {
  const [formData, setFormData] = useState({})
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      title="فرم جدید"
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            انصراف
          </Button>
          <Button variant="primary" onClick={() => onSubmit(formData)}>
            ذخیره
          </Button>
        </>
      }
    >
      <Input
        label="نام"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />
    </Modal>
  )
}

// مودیال تایید
function ConfirmModal({ open, onClose, onConfirm, message }) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title="تایید"
      size="sm"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            انصراف
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            تایید
          </Button>
        </>
      }
    >
      <p>{message}</p>
    </Modal>
  )
}
```

## Table

کامپوننت جدول Responsive که به صورت خودکار در موبایل به Card تبدیل می‌شود.

### استفاده پایه

```jsx
import { Table } from '../ui'

const columns = [
  { key: 'name', label: 'نام' },
  { key: 'email', label: 'ایمیل' },
  { key: 'role', label: 'نقش' }
]

const data = [
  { id: 1, name: 'علی', email: 'ali@example.com', role: 'کاربر' },
  { id: 2, name: 'رضا', email: 'reza@example.com', role: 'ادمین' }
]

<Table columns={columns} data={data} />
```

### با Custom Render

```jsx
const columns = [
  { key: 'name', label: 'نام' },
  { 
    key: 'status', 
    label: 'وضعیت',
    render: (value) => (
      <Badge variant={value === 'active' ? 'success' : 'error'}>
        {value === 'active' ? 'فعال' : 'غیرفعال'}
      </Badge>
    )
  },
  {
    key: 'actions',
    label: 'اقدامات',
    render: (value, row) => (
      <>
        <Button size="sm" onClick={() => handleEdit(row)}>ویرایش</Button>
        <Button size="sm" variant="danger" onClick={() => handleDelete(row)}>
          حذف
        </Button>
      </>
    )
  }
]
```

### با Mobile Card سفارشی

```jsx
<Table
  columns={columns}
  data={data}
  renderMobileCard={(row) => (
    <Card>
      <CardHeader>
        <h3>{row.name}</h3>
      </CardHeader>
      <CardBody>
        <p>ایمیل: {row.email}</p>
        <p>نقش: {row.role}</p>
      </CardBody>
      <CardActions>
        <Button size="sm">ویرایش</Button>
        <Button size="sm" variant="danger">حذف</Button>
      </CardActions>
    </Card>
  )}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `columns` | `array` | `[]` | تعریف ستون‌ها |
| `data` | `array` | `[]` | داده‌های جدول |
| `renderMobileCard` | `function` | - | Render سفارشی برای موبایل |
| `emptyMessage` | `string` | `'داده‌ای برای نمایش وجود ندارد'` | پیام خالی |
| `className` | `string` | `''` | کلاس‌های اضافی |

### Column Definition

```typescript
interface Column {
  key: string              // کلید فیلد در data
  label: string            // برچسب ستون
  render?: (value, row, index) => ReactNode  // Render سفارشی
  mobileLabel?: string     // برچسب در موبایل (اختیاری)
  className?: string       // کلاس CSS برای ستون
}
```

### مثال‌های پیشرفته

```jsx
// جدول با Pagination
function DataTable({ data, onPageChange, currentPage, totalPages }) {
  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'نام' },
    { key: 'email', label: 'ایمیل' }
  ]
  
  return (
    <>
      <Table columns={columns} data={data} />
      <div className="pagination">
        <Button 
          disabled={currentPage === 1}
          onClick={() => onPageChange(currentPage - 1)}
        >
          قبلی
        </Button>
        <span>صفحه {currentPage} از {totalPages}</span>
        <Button 
          disabled={currentPage === totalPages}
          onClick={() => onPageChange(currentPage + 1)}
        >
          بعدی
        </Button>
      </div>
    </>
  )
}

// جدول با Sort
function SortableTable({ data }) {
  const [sortKey, setSortKey] = useState(null)
  const [sortOrder, setSortOrder] = useState('asc')
  
  const handleSort = (key) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortOrder('asc')
    }
  }
  
  const sortedData = [...data].sort((a, b) => {
    if (sortOrder === 'asc') {
      return a[sortKey] > b[sortKey] ? 1 : -1
    } else {
      return a[sortKey] < b[sortKey] ? 1 : -1
    }
  })
  
  const columns = [
    { 
      key: 'name', 
      label: 'نام',
      render: (value) => (
        <button onClick={() => handleSort('name')}>
          {value} {sortKey === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
        </button>
      )
    }
  ]
  
  return <Table columns={columns} data={sortedData} />
}
```

## Loading

کامپوننت نمایش حالت بارگذاری.

### Spinner

```jsx
import { Loading } from '../ui'

<Loading />
<Loading size="sm" />
<Loading size="md" />
<Loading size="lg" />
<Loading text="در حال بارگذاری..." />
```

### Variants

```jsx
<Loading variant="spinner" />
<Loading variant="dots" />
<Loading variant="pulse" />
```

### Loading Overlay

```jsx
import { LoadingOverlay } from '../ui'

<LoadingOverlay loading={isLoading}>
  <YourContent />
</LoadingOverlay>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | اندازه |
| `variant` | `'spinner' \| 'dots' \| 'pulse'` | `'spinner'` | نوع نمایش |
| `text` | `string` | - | متن نمایش |
| `className` | `string` | `''` | کلاس‌های اضافی |

### مثال‌های پیشرفته

```jsx
// Loading در Button
function SubmitButton({ loading, onClick }) {
  return (
    <Button onClick={onClick} loading={loading}>
      {loading ? 'در حال ارسال...' : 'ارسال'}
    </Button>
  )
}

// Loading در Card
function DataCard({ data, loading }) {
  if (loading) {
    return (
      <Card>
        <CardBody>
          <Loading text="در حال بارگذاری داده‌ها..." />
        </CardBody>
      </Card>
    )
  }
  
  return <Card>{/* محتوا */}</Card>
}
```

## EmptyState

کامپوننت نمایش حالت خالی.

### استفاده پایه

```jsx
import { EmptyState, Button } from '../ui'
import { Inbox } from 'lucide-react'

<EmptyState
  title="داده‌ای وجود ندارد"
  description="هنوز هیچ داده‌ای اضافه نشده است"
  icon={<Inbox size={48} />}
  action={<Button>افزودن داده</Button>}
/>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | - | عنوان |
| `description` | `string` | - | توضیحات |
| `icon` | `ReactNode` | - | آیکون |
| `action` | `ReactNode` | - | دکمه اقدام |
| `className` | `string` | `''` | کلاس‌های اضافی |

### مثال‌های پیشرفته

```jsx
// EmptyState در Table
function DataTable({ data, loading }) {
  if (loading) {
    return <Loading />
  }
  
  if (data.length === 0) {
    return (
      <EmptyState
        title="هیچ داده‌ای یافت نشد"
        description="لطفاً فیلترها را تغییر دهید یا داده جدید اضافه کنید"
        icon={<Search size={48} />}
        action={<Button onClick={handleAdd}>افزودن داده</Button>}
      />
    )
  }
  
  return <Table columns={columns} data={data} />
}

// EmptyState در List
function ItemList({ items }) {
  if (items.length === 0) {
    return (
      <EmptyState
        title="لیست خالی است"
        description="برای شروع، اولین آیتم را اضافه کنید"
        action={<Button>افزودن آیتم</Button>}
      />
    )
  }
  
  return (
    <div>
      {items.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  )
}
```

## ترکیب کامپوننت‌ها

### مثال کامل: Data Table با Modal

```jsx
function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  const columns = [
    { key: 'name', label: 'نام' },
    { key: 'email', label: 'ایمیل' },
    {
      key: 'actions',
      label: 'اقدامات',
      render: (value, row) => (
        <>
          <Button size="sm" onClick={() => handleEdit(row)}>
            ویرایش
          </Button>
          <Button 
            size="sm" 
            variant="danger"
            onClick={() => handleDelete(row)}
          >
            حذف
          </Button>
        </>
      )
    }
  ]
  
  if (loading) {
    return <Loading text="در حال بارگذاری..." />
  }
  
  if (users.length === 0) {
    return (
      <EmptyState
        title="هیچ کاربری وجود ندارد"
        action={<Button onClick={() => setIsModalOpen(true)}>افزودن کاربر</Button>}
      />
    )
  }
  
  return (
    <>
      <Table columns={columns} data={users} />
      <Modal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="افزودن کاربر"
      >
        {/* فرم */}
      </Modal>
    </>
  )
}
```

## مراحل بعدی

- [Theme و Customization](./theme-customization.md)
- [معماری فرانت‌اند](../03-frontend/architecture.md)

