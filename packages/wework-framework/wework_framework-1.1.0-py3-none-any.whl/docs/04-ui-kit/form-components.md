# کامپوننت‌های فرم

این بخش شامل کامپوننت‌های فرم UI Kit است که برای ساخت فرم‌ها استفاده می‌شوند.

## Input

کامپوننت فیلد ورودی متن.

### استفاده پایه

```jsx
import { Input } from '../ui'

function MyForm() {
  const [value, setValue] = useState('')
  
  return (
    <Input
      label="نام"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="نام خود را وارد کنید"
    />
  )
}
```

### با Validation

```jsx
const [error, setError] = useState('')

<Input
  label="ایمیل"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={error}
  helperText="ایمیل خود را وارد کنید"
/>
```

### Types

```jsx
<Input type="text" label="متن" />
<Input type="email" label="ایمیل" />
<Input type="password" label="رمز عبور" />
<Input type="number" label="عدد" />
<Input type="tel" label="تلفن" />
<Input type="url" label="لینک" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | برچسب فیلد |
| `type` | `string` | `'text'` | نوع فیلد |
| `value` | `string` | - | مقدار فیلد |
| `onChange` | `function` | - | Handler تغییر |
| `error` | `string` | - | پیام خطا |
| `helperText` | `string` | - | متن راهنما |
| `fullWidth` | `boolean` | `false` | عرض کامل |
| `disabled` | `boolean` | `false` | غیرفعال |
| `required` | `boolean` | `false` | اجباری |
| `placeholder` | `string` | - | متن placeholder |

### مثال‌های پیشرفته

```jsx
// Input با آیکون
import { Input } from '../ui'
import { Search } from 'lucide-react'

<div style={{ position: 'relative' }}>
  <Search style={{ position: 'absolute', right: '10px', top: '50%' }} />
  <Input placeholder="جستجو..." />
</div>

// Input با Validation
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

<Input
  label="ایمیل"
  type="email"
  value={email}
  onChange={(e) => {
    setEmail(e.target.value)
    if (!validateEmail(e.target.value)) {
      setError('ایمیل معتبر نیست')
    } else {
      setError('')
    }
  }}
  error={error}
/>
```

## Select

کامپوننت فیلد انتخاب.

### استفاده پایه

```jsx
import { Select } from '../ui'

function MyForm() {
  const [value, setValue] = useState('')
  
  return (
    <Select
      label="انتخاب کنید"
      value={value}
      onChange={(e) => setValue(e.target.value)}
    >
      <option value="">انتخاب کنید</option>
      <option value="1">گزینه ۱</option>
      <option value="2">گزینه ۲</option>
      <option value="3">گزینه ۳</option>
    </Select>
  )
}
```

### با Validation

```jsx
<Select
  label="دسته‌بندی"
  value={category}
  onChange={(e) => setCategory(e.target.value)}
  error={!category ? 'لطفاً یک گزینه انتخاب کنید' : ''}
  required
>
  <option value="">انتخاب کنید</option>
  <option value="cat1">دسته ۱</option>
  <option value="cat2">دسته ۲</option>
</Select>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | برچسب فیلد |
| `value` | `string` | - | مقدار انتخاب شده |
| `onChange` | `function` | - | Handler تغییر |
| `error` | `string` | - | پیام خطا |
| `helperText` | `string` | - | متن راهنما |
| `fullWidth` | `boolean` | `false` | عرض کامل |
| `disabled` | `boolean` | `false` | غیرفعال |
| `required` | `boolean` | `false` | اجباری |
| `children` | `ReactNode` | - | Option elements |

## Textarea

کامپوننت فیلد متن چندخطی.

### استفاده پایه

```jsx
import { Textarea } from '../ui'

function MyForm() {
  const [value, setValue] = useState('')
  
  return (
    <Textarea
      label="توضیحات"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      rows={5}
      placeholder="توضیحات خود را وارد کنید"
    />
  )
}
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | - | برچسب فیلد |
| `value` | `string` | - | مقدار فیلد |
| `onChange` | `function` | - | Handler تغییر |
| `error` | `string` | - | پیام خطا |
| `helperText` | `string` | - | متن راهنما |
| `rows` | `number` | `4` | تعداد خطوط |
| `fullWidth` | `boolean` | `false` | عرض کامل |
| `disabled` | `boolean` | `false` | غیرفعال |
| `required` | `boolean` | `false` | اجباری |
| `placeholder` | `string` | - | متن placeholder |

## Form Components

کامپوننت‌های کمکی برای ساخت فرم‌ها.

### FormGroup

گروه‌بندی فیلدهای فرم.

```jsx
import { FormGroup, Input } from '../ui'

<FormGroup>
  <Input label="نام" />
  <Input label="نام خانوادگی" />
</FormGroup>
```

### FormRow

نمایش فیلدها در یک ردیف (در دسکتاپ).

```jsx
import { FormRow, Input } from '../ui'

<FormRow columns={2}>
  <Input label="نام" />
  <Input label="نام خانوادگی" />
</FormRow>

<FormRow columns={3}>
  <Input label="کد پستی" />
  <Input label="شهر" />
  <Input label="استان" />
</FormRow>
```

### FormActions

بخش دکمه‌های اقدام فرم.

```jsx
import { FormActions, Button } from '../ui'

<FormActions>
  <Button variant="secondary">انصراف</Button>
  <Button variant="primary">ذخیره</Button>
</FormActions>
```

### مثال کامل فرم

```jsx
import { useState } from 'react'
import { 
  Card, CardHeader, CardBody, CardActions,
  Input, Select, Textarea, FormRow, FormActions,
  Button 
} from '../ui'

function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [errors, setErrors] = useState({})
  
  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value })
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' })
    }
  }
  
  const validate = () => {
    const newErrors = {}
    if (!formData.name) newErrors.name = 'نام الزامی است'
    if (!formData.email) newErrors.email = 'ایمیل الزامی است'
    if (!formData.message) newErrors.message = 'پیام الزامی است'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      // ارسال فرم
      console.log('Form submitted:', formData)
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
          
          <Select
            label="موضوع"
            value={formData.subject}
            onChange={handleChange('subject')}
          >
            <option value="">انتخاب کنید</option>
            <option value="support">پشتیبانی</option>
            <option value="sales">فروش</option>
            <option value="other">سایر</option>
          </Select>
          
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
            <Button type="button" variant="secondary">انصراف</Button>
            <Button type="submit" variant="primary">ارسال</Button>
          </FormActions>
        </CardActions>
      </form>
    </Card>
  )
}
```

## مراحل بعدی

- [کامپوننت‌های پیشرفته](./advanced-components.md)
- [Theme و Customization](./theme-customization.md)

