# UI Kit Documentation

این UI Kit مجموعه کامپوننت‌های قابل استفاده مجدد برای پروژه است که بر اساس اصول طراحی مدرن و بهترین روش‌های UX/UI ساخته شده است.

## ویژگی‌ها

- ✅ کامپوننت‌های قابل استفاده مجدد
- ✅ طراحی Responsive و Mobile-First
- ✅ پشتیبانی از RTL (راست به چپ)
- ✅ Theme System یکپارچه
- ✅ TypeScript Ready (JSDoc comments)
- ✅ Accessible (ARIA support)
- ✅ Performance Optimized

## نصب و استفاده

```jsx
import { Button, Card, Modal, Input } from '../ui'

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <h3>عنوان</h3>
      </CardHeader>
      <CardBody>
        <Input label="نام" placeholder="نام خود را وارد کنید" />
        <Button variant="primary">ذخیره</Button>
      </CardBody>
    </Card>
  )
}
```

## کامپوننت‌ها

### Button

دکمه با انواع مختلف و حالت‌های مختلف

```jsx
<Button variant="primary" size="md" loading={false}>
  کلیک کنید
</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost'
- `size`: 'sm' | 'md' | 'lg'
- `loading`: boolean
- `disabled`: boolean

### Card

کارت برای نمایش محتوا

```jsx
<Card hover>
  <CardHeader>عنوان</CardHeader>
  <CardBody>محتوا</CardBody>
  <CardActions>
    <Button>اقدام</Button>
  </CardActions>
</Card>
```

**Components:**
- `Card` - Container
- `CardHeader` - Header section
- `CardBody` - Main content
- `CardFooter` - Footer section
- `CardActions` - Action buttons

### Modal

مودیال برای نمایش دیالوگ‌ها

```jsx
<Modal
  open={isOpen}
  onClose={() => setIsOpen(false)}
  title="عنوان مودیال"
  size="md"
>
  محتوای مودیال
</Modal>
```

**Props:**
- `open`: boolean
- `onClose`: function
- `title`: string
- `size`: 'sm' | 'md' | 'lg' | 'xl' | 'full'
- `closeOnBackdrop`: boolean

### Input / Select / Textarea

فیلدهای ورودی فرم

```jsx
<Input
  label="نام"
  type="text"
  value={value}
  onChange={(e) => setValue(e.target.value)}
  error={error}
  helperText="راهنما"
  fullWidth
/>

<Select label="انتخاب" value={value} onChange={handleChange}>
  <option value="1">گزینه ۱</option>
</Select>
```

### Table

جدول Responsive با نمایش کارت در موبایل

```jsx
<Table
  columns={[
    { key: 'name', label: 'نام' },
    { key: 'email', label: 'ایمیل' },
  ]}
  data={users}
  renderMobileCard={(row) => <CustomCard data={row} />}
/>
```

### Badge

نشانگر وضعیت

```jsx
<Badge variant="success" size="md">
  فعال
</Badge>
```

**Props:**
- `variant`: 'success' | 'error' | 'warning' | 'info' | 'muted'
- `size`: 'sm' | 'md' | 'lg'

### Loading

نمایش حالت بارگذاری

```jsx
<Loading size="md" variant="spinner" text="در حال بارگذاری..." />
<LoadingOverlay loading={isLoading}>
  <YourContent />
</LoadingOverlay>
```

### EmptyState

نمایش حالت خالی

```jsx
<EmptyState
  title="داده‌ای وجود ندارد"
  description="توضیحات بیشتر"
  icon={<Icon />}
  action={<Button>اقدام</Button>}
/>
```

### Form Components

کامپوننت‌های فرم

```jsx
<FormGroup>
  <Input label="نام" />
</FormGroup>

<FormRow columns={2}>
  <Input label="نام" />
  <Input label="نام خانوادگی" />
</FormRow>

<FormActions>
  <Button variant="secondary">انصراف</Button>
  <Button variant="primary">ذخیره</Button>
</FormActions>
```

## Hooks

### useInfiniteScroll

برای پیاده‌سازی Infinite Scroll

```jsx
const { lastElementRef } = useInfiniteScroll(
  loadMore,
  hasMore,
  loading,
  { threshold: 0.1, rootMargin: '100px' }
)

<div ref={lastElementRef}>آخرین آیتم</div>
```

### useResponsive

برای تشخیص اندازه صفحه

```jsx
const { isMobile, isTablet, isDesktop, width } = useResponsive()
```

## Theme

```jsx
import { theme } from '../ui'

// استفاده از theme
const color = theme.colors.bg.primary
const spacing = theme.spacing.md
```

## Best Practices

1. **همیشه از کامپوننت‌های UI Kit استفاده کنید** - از نوشتن استایل‌های سفارشی خودداری کنید
2. **Responsive Design** - همیشه موبایل را در نظر بگیرید
3. **Accessibility** - از label و aria-label استفاده کنید
4. **Performance** - از React.memo برای کامپوننت‌های سنگین استفاده کنید
5. **Consistency** - از variant و size های استاندارد استفاده کنید

## Mobile Considerations

- تمام کامپوننت‌ها به صورت خودکار در موبایل responsive هستند
- Table به صورت خودکار در موبایل به Card تبدیل می‌شود
- FormRow در موبایل به صورت عمودی نمایش داده می‌شود
- Modal در موبایل full-screen می‌شود

## Contributing

برای اضافه کردن کامپوننت جدید:

1. کامپوننت را در `frontend/src/ui/` ایجاد کنید
2. CSS را در فایل جداگانه اضافه کنید
3. کامپوننت را در `index.js` export کنید
4. Documentation اضافه کنید
5. Mobile responsive را تست کنید

