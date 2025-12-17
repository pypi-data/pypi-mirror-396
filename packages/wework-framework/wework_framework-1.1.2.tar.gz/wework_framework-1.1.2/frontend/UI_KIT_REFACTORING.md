# UI Kit Refactoring - خلاصه تغییرات

## ✅ کارهای انجام شده

### 1. ایجاد UI Kit پایه
- ✅ **Button** - دکمه با انواع variant و size
- ✅ **Card** - کارت با بخش‌های Header, Body, Footer, Actions
- ✅ **Badge** - نشانگر وضعیت
- ✅ **Input/Select/Textarea** - فیلدهای ورودی فرم
- ✅ **Modal** - مودیال با سایزهای مختلف
- ✅ **Table** - جدول Responsive با نمایش کارت در موبایل
- ✅ **EmptyState** - نمایش حالت خالی
- ✅ **Loading** - نمایش حالت بارگذاری
- ✅ **Form Components** - FormGroup, FormRow, FormActions

### 2. Hooks
- ✅ **useInfiniteScroll** - برای پیاده‌سازی Infinite Scroll
- ✅ **useResponsive** - برای تشخیص اندازه صفحه

### 3. Theme System
- ✅ Design Tokens (colors, spacing, borderRadius, shadows, transitions)
- ✅ Breakpoints برای Responsive Design
- ✅ Z-index management

### 4. کامپوننت‌های Refactor شده
- ✅ **BotManagement** - کاملاً با UI Kit refactor شده
  - استفاده از Card, Button, Badge, Modal
  - Infinite Scroll پیاده‌سازی شده
  - Mobile Responsive
  - استفاده از Form Components

### 5. ویژگی‌های کلیدی
- ✅ **Mobile-First Design** - تمام کامپوننت‌ها responsive هستند
- ✅ **RTL Support** - پشتیبانی کامل از راست به چپ
- ✅ **Accessibility** - استفاده از ARIA attributes
- ✅ **Performance** - بهینه‌سازی شده با React.forwardRef
- ✅ **Reusable** - کامپوننت‌ها قابل استفاده مجدد در پروژه‌های دیگر

## 📁 ساختار فایل‌ها

```
frontend/src/
├── ui/
│   ├── Button.jsx & Button.css
│   ├── Card.jsx & Card.css
│   ├── Badge.jsx & Badge.css
│   ├── Input.jsx & Input.css
│   ├── Modal.jsx & Modal.css
│   ├── Table.jsx & Table.css
│   ├── EmptyState.jsx & EmptyState.css
│   ├── Loading.jsx & Loading.css
│   ├── Form.jsx & Form.css
│   ├── theme.js
│   ├── index.js
│   └── README.md
├── hooks/
│   ├── useInfiniteScroll.js
│   └── useResponsive.js
└── components/
    └── BotManagement.jsx (refactored)
```

## 🎯 نحوه استفاده

### مثال ساده
```jsx
import { Button, Card, CardHeader, CardBody } from '../ui'

function MyComponent() {
  return (
    <Card hover>
      <CardHeader>
        <h3>عنوان</h3>
      </CardHeader>
      <CardBody>
        <Button variant="primary">کلیک کنید</Button>
      </CardBody>
    </Card>
  )
}
```

### مثال با Infinite Scroll
```jsx
import { Card } from '../ui'
import { useInfiniteScroll } from '../hooks/useInfiniteScroll'

function ListComponent() {
  const { lastElementRef } = useInfiniteScroll(loadMore, hasMore, loading)
  
  return (
    <div>
      {items.map((item, index) => (
        <Card
          key={item.id}
          ref={index === items.length - 1 ? lastElementRef : null}
        >
          {item.content}
        </Card>
      ))}
    </div>
  )
}
```

### مثال با Table (Responsive)
```jsx
import { Table, Badge, Button } from '../ui'

function UsersTable({ users }) {
  const columns = [
    { key: 'name', label: 'نام', mobileLabel: 'نام کاربر' },
    { key: 'email', label: 'ایمیل' },
    {
      key: 'status',
      label: 'وضعیت',
      render: (value) => <Badge variant={value === 'active' ? 'success' : 'muted'}>
        {value === 'active' ? 'فعال' : 'غیرفعال'}
      </Badge>
    },
  ]
  
  return <Table columns={columns} data={users} />
}
```

## 📱 Mobile Features

### Table به Card تبدیل می‌شود
- در موبایل (عرض < 768px) جدول به صورت خودکار به کارت تبدیل می‌شود
- هر ردیف جدول به یک کارت تبدیل می‌شود
- می‌توانید با `renderMobileCard` نمایش سفارشی داشته باشید

### FormRow در موبایل عمودی می‌شود
- در موبایل تمام فیلدها به صورت عمودی نمایش داده می‌شوند
- دکمه‌ها در موبایل full-width می‌شوند

### Modal در موبایل
- Modal در موبایل full-screen می‌شود
- Padding و spacing بهینه می‌شود

## 🔄 کامپوننت‌های بعدی برای Refactor

کامپوننت‌های زیر می‌توانند با UI Kit refactor شوند:

1. **AdminUsers** - استفاده از Table component
2. **StrategyList** - استفاده از Card و Infinite Scroll (قبلاً پیاده شده)
3. **ExchangeManagement** - استفاده از Card و Form components
4. **AdminPayments** - استفاده از Table component
5. **AdminSubscriptions** - استفاده از Table component
6. **LiveTradesHistory** - استفاده از Table component

## 🎨 Theme Customization

```jsx
import { theme } from '../ui'

// استفاده از theme
const styles = {
  backgroundColor: theme.colors.bg.primary,
  padding: theme.spacing.md,
  borderRadius: theme.borderRadius.md,
  boxShadow: theme.shadows.md,
}
```

## 📝 Best Practices

1. **همیشه از UI Kit استفاده کنید** - از نوشتن استایل‌های سفارشی خودداری کنید
2. **Mobile First** - همیشه موبایل را در نظر بگیرید
3. **Consistency** - از variant و size های استاندارد استفاده کنید
4. **Accessibility** - از label و aria-label استفاده کنید
5. **Performance** - از React.memo برای کامپوننت‌های سنگین استفاده کنید

## 🚀 مراحل بعدی

1. Refactor سایر کامپوننت‌ها با UI Kit
2. اضافه کردن Storybook برای Documentation
3. اضافه کردن Unit Tests
4. بهینه‌سازی Performance
5. اضافه کردن Dark/Light Mode (در صورت نیاز)

## 📚 Documentation

برای جزئیات بیشتر به `frontend/src/ui/README.md` مراجعه کنید.

