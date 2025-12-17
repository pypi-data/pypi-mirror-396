# کامپوننت‌های پایه

این بخش شامل کامپوننت‌های پایه UI Kit است که در تمام پروژه‌ها استفاده می‌شوند.

## Button

کامپوننت دکمه با انواع مختلف و حالت‌های مختلف.

### استفاده پایه

```jsx
import { Button } from '../ui'

function MyComponent() {
  return (
    <div>
      <Button>دکمه پیش‌فرض</Button>
      <Button variant="primary">دکمه اصلی</Button>
      <Button variant="secondary">دکمه ثانویه</Button>
    </div>
  )
}
```

### Variants

```jsx
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="success">Success</Button>
<Button variant="warning">Warning</Button>
<Button variant="danger">Danger</Button>
<Button variant="ghost">Ghost</Button>
```

### Sizes

```jsx
<Button size="sm">کوچک</Button>
<Button size="md">متوسط</Button>
<Button size="lg">بزرگ</Button>
```

### States

```jsx
<Button disabled>غیرفعال</Button>
<Button loading>در حال بارگذاری</Button>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'success' \| 'warning' \| 'danger' \| 'ghost'` | `'primary'` | نوع دکمه |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | اندازه دکمه |
| `disabled` | `boolean` | `false` | غیرفعال کردن دکمه |
| `loading` | `boolean` | `false` | نمایش حالت بارگذاری |
| `className` | `string` | `''` | کلاس‌های اضافی |
| `children` | `ReactNode` | - | محتوای دکمه |
| `onClick` | `function` | - | Handler کلیک |

### مثال‌های پیشرفته

```jsx
// دکمه با آیکون
import { Button } from '../ui'
import { Save } from 'lucide-react'

<Button>
  <Save size={16} />
  ذخیره
</Button>

// دکمه Full Width
<Button style={{ width: '100%' }}>ذخیره</Button>

// دکمه با Handler
<Button onClick={() => handleSave()}>
  ذخیره
</Button>
```

## Card

کامپوننت کارت برای نمایش محتوا در یک Container.

### استفاده پایه

```jsx
import { Card, CardHeader, CardBody, CardFooter } from '../ui'

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <h3>عنوان کارت</h3>
      </CardHeader>
      <CardBody>
        <p>محتوای کارت</p>
      </CardBody>
      <CardFooter>
        <Button>اقدام</Button>
      </CardFooter>
    </Card>
  )
}
```

### Variants

```jsx
<Card variant="default">پیش‌فرض</Card>
<Card variant="outlined">با خط دور</Card>
<Card variant="elevated">با سایه</Card>
```

### Hover Effect

```jsx
<Card hover>
  کارت با افکت Hover
</Card>
```

### Components

- **Card**: Container اصلی
- **CardHeader**: بخش هدر
- **CardBody**: بخش محتوا
- **CardFooter**: بخش فوتر
- **CardActions**: بخش دکمه‌های اقدام

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'default' \| 'outlined' \| 'elevated'` | `'default'` | نوع کارت |
| `hover` | `boolean` | `false` | فعال کردن افکت Hover |
| `className` | `string` | `''` | کلاس‌های اضافی |

### مثال‌های پیشرفته

```jsx
// کارت با تصویر
<Card>
  <img src="/image.jpg" alt="تصویر" />
  <CardBody>
    <h3>عنوان</h3>
    <p>توضیحات</p>
  </CardBody>
</Card>

// کارت با Actions
<Card>
  <CardHeader>عنوان</CardHeader>
  <CardBody>محتوا</CardBody>
  <CardActions>
    <Button variant="secondary">انصراف</Button>
    <Button variant="primary">ذخیره</Button>
  </CardActions>
</Card>
```

## Badge

کامپوننت نشانگر وضعیت برای نمایش اطلاعات کوتاه.

### استفاده پایه

```jsx
import { Badge } from '../ui'

<Badge>فعال</Badge>
<Badge variant="success">موفق</Badge>
<Badge variant="error">خطا</Badge>
```

### Variants

```jsx
<Badge variant="success">موفق</Badge>
<Badge variant="error">خطا</Badge>
<Badge variant="warning">هشدار</Badge>
<Badge variant="info">اطلاعات</Badge>
<Badge variant="muted">خاموش</Badge>
```

### Sizes

```jsx
<Badge size="sm">کوچک</Badge>
<Badge size="md">متوسط</Badge>
<Badge size="lg">بزرگ</Badge>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'success' \| 'error' \| 'warning' \| 'info' \| 'muted'` | `'info'` | نوع Badge |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | اندازه Badge |
| `className` | `string` | `''` | کلاس‌های اضافی |
| `children` | `ReactNode` | - | محتوای Badge |

### مثال‌های پیشرفته

```jsx
// Badge با آیکون
import { Badge } from '../ui'
import { Check } from 'lucide-react'

<Badge variant="success">
  <Check size={12} />
  تایید شده
</Badge>

// Badge در Button
<Button>
  اعلان‌ها
  <Badge variant="error">5</Badge>
</Button>
```

## مراحل بعدی

- [کامپوننت‌های فرم](./form-components.md)
- [کامپوننت‌های پیشرفته](./advanced-components.md)

