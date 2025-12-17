# معرفی UI Kit

UI Kit فریمورک WeWork مجموعه کامپوننت‌های React قابل استفاده مجدد و آماده برای استفاده است که با بهترین روش‌های طراحی و UX ساخته شده‌اند.

## ویژگی‌های کلیدی

- ✅ **کامپوننت‌های آماده**: بیش از 20 کامپوننت آماده استفاده
- ✅ **Responsive Design**: تمام کامپوننت‌ها به صورت خودکار برای موبایل، تبلت و دسکتاپ بهینه شده‌اند
- ✅ **RTL Support**: پشتیبانی کامل از راست به چپ برای زبان‌های فارسی و عربی
- ✅ **Theme System**: سیستم Theme یکپارچه و قابل سفارشی‌سازی
- ✅ **Accessibility**: رعایت استانداردهای دسترسی‌پذیری (ARIA)
- ✅ **TypeScript Ready**: کامپوننت‌ها با JSDoc آماده برای TypeScript
- ✅ **Performance**: بهینه‌سازی شده برای عملکرد بالا

## نصب و استفاده

کامپوننت‌های UI Kit در پوشه `frontend/src/ui/` قرار دارند و به صورت مستقیم قابل استفاده هستند:

```jsx
import { Button, Card, Modal, Input } from '../ui'

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <h3>عنوان کارت</h3>
      </CardHeader>
      <CardBody>
        <Input label="نام" placeholder="نام خود را وارد کنید" />
        <Button variant="primary">ذخیره</Button>
      </CardBody>
    </Card>
  )
}
```

## ساختار کامپوننت‌ها

تمام کامپوننت‌ها از یک ساختار یکپارچه پیروی می‌کنند:

```
ui/
├── Button.jsx          # دکمه با انواع مختلف
├── Button.css
├── Card.jsx            # کارت و Container
├── Card.css
├── Modal.jsx           # مودیال و دیالوگ
├── Modal.css
├── Input.jsx           # فیلدهای ورودی (Input, Select, Textarea)
├── Input.css
├── Table.jsx           # جدول Responsive
├── Table.css
├── Badge.jsx           # نشانگر وضعیت
├── Badge.css
├── Loading.jsx         # نمایش حالت بارگذاری
├── Loading.css
├── EmptyState.jsx      # نمایش حالت خالی
├── EmptyState.css
├── Form.jsx            # کامپوننت‌های فرم
├── Form.css
├── theme.js            # تنظیمات Theme
└── index.js            # Export مرکزی
```

## دسته‌بندی کامپوننت‌ها

### کامپوننت‌های پایه
- **Button**: دکمه با انواع مختلف
- **Badge**: نشانگر وضعیت
- **Card**: Container برای محتوا

### کامپوننت‌های فرم
- **Input**: فیلد ورودی متن
- **Select**: فیلد انتخاب
- **Textarea**: فیلد متن چندخطی
- **Form**: کامپوننت‌های کمکی فرم

### کامپوننت‌های پیشرفته
- **Modal**: دیالوگ و مودیال
- **Table**: جدول Responsive
- **Loading**: نمایش حالت بارگذاری
- **EmptyState**: نمایش حالت خالی

## سیستم Theme

UI Kit از یک سیستم Theme یکپارچه استفاده می‌کند که در `theme.js` تعریف شده است:

```jsx
import { theme } from '../ui'

// استفاده از رنگ‌ها
const primaryColor = theme.colors.primary

// استفاده از فاصله‌گذاری
const spacing = theme.spacing.md

// استفاده از تایپوگرافی
const fontSize = theme.typography.h1.fontSize
```

## Responsive Design

تمام کامپوننت‌ها به صورت خودکار برای اندازه‌های مختلف صفحه بهینه شده‌اند:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

برای مثال، کامپوننت Table به صورت خودکار در موبایل به Card تبدیل می‌شود.

## دسترسی‌پذیری (Accessibility)

تمام کامپوننت‌ها با رعایت استانداردهای دسترسی‌پذیری ساخته شده‌اند:

- استفاده از ARIA attributes
- پشتیبانی از صفحه‌خوان‌ها
- Navigation با کیبورد
- Focus management

## بهترین روش‌ها

1. **همیشه از کامپوننت‌های UI Kit استفاده کنید**: از نوشتن استایل‌های سفارشی خودداری کنید
2. **Responsive First**: همیشه موبایل را در نظر بگیرید
3. **Accessibility**: از label و aria-label استفاده کنید
4. **Performance**: از React.memo برای کامپوننت‌های سنگین استفاده کنید
5. **Consistency**: از variant و size های استاندارد استفاده کنید

## مراحل بعدی

- [کامپوننت‌های پایه](./basic-components.md)
- [کامپوننت‌های فرم](./form-components.md)
- [کامپوننت‌های پیشرفته](./advanced-components.md)
- [Theme و Customization](./theme-customization.md)

