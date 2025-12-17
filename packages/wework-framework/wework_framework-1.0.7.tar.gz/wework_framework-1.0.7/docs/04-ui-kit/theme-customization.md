# Theme و Customization

این بخش نحوه سفارشی‌سازی Theme و استایل‌های UI Kit را توضیح می‌دهد.

## سیستم Theme

Theme در `frontend/src/ui/theme.js` تعریف شده است:

```javascript
export const theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    // ...
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  typography: {
    // ...
  },
  breakpoints: {
    mobile: '768px',
    tablet: '1024px',
    desktop: '1200px',
  }
}
```

## استفاده از Theme

### در JavaScript

```jsx
import { theme } from '../ui'

const style = {
  color: theme.colors.primary,
  padding: theme.spacing.md,
  fontSize: theme.typography.body.fontSize
}
```

### در CSS

```css
/* استفاده از CSS Variables */
.my-component {
  color: var(--color-primary);
  padding: var(--spacing-md);
}
```

## سفارشی‌سازی Theme

### تغییر Theme اصلی

```javascript
// frontend/src/ui/theme.js
export const theme = {
  colors: {
    primary: '#your-color',  // تغییر رنگ اصلی
    // ...
  },
  // ...
}
```

### ایجاد Theme سفارشی

```javascript
// frontend/src/ui/custom-theme.js
import { theme as baseTheme } from './theme'

export const customTheme = {
  ...baseTheme,
  colors: {
    ...baseTheme.colors,
    primary: '#custom-color',
  }
}
```

## CSS Variables

UI Kit از CSS Variables استفاده می‌کند:

```css
:root {
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --spacing-md: 1rem;
  /* ... */
}
```

### تغییر CSS Variables

```css
/* در فایل CSS خود */
:root {
  --color-primary: #your-color;
  --spacing-md: 1.5rem;
}
```

## Customization کامپوننت‌ها

### با className

```jsx
<Button className="my-custom-button">
  دکمه سفارشی
</Button>
```

```css
.my-custom-button {
  background: linear-gradient(45deg, #f0f, #0ff);
  border-radius: 20px;
}
```

### با style prop

```jsx
<Button style={{ 
  backgroundColor: '#custom-color',
  borderRadius: '10px'
}}>
  دکمه سفارشی
</Button>
```

### با CSS Modules

```jsx
// MyComponent.module.css
.customButton {
  background: #custom-color;
}

// MyComponent.jsx
import styles from './MyComponent.module.css'

<Button className={styles.customButton}>
  دکمه سفارشی
</Button>
```

## Dark Mode

### پیاده‌سازی Dark Mode

```javascript
// theme.js
export const themes = {
  light: {
    colors: {
      bg: '#ffffff',
      text: '#000000',
      // ...
    }
  },
  dark: {
    colors: {
      bg: '#1a1a1a',
      text: '#ffffff',
      // ...
    }
  }
}
```

### استفاده

```jsx
import { themes } from '../ui'

const [theme, setTheme] = useState('light')

<div style={{ 
  backgroundColor: themes[theme].colors.bg,
  color: themes[theme].colors.text
}}>
  محتوا
</div>
```

## Responsive Customization

### با Media Queries

```css
.my-component {
  padding: 1rem;
}

@media (max-width: 768px) {
  .my-component {
    padding: 0.5rem;
  }
}
```

### با useResponsive Hook

```jsx
import { useResponsive } from '../hooks/useResponsive'

function MyComponent() {
  const { isMobile, isTablet, isDesktop } = useResponsive()
  
  return (
    <div style={{
      padding: isMobile ? '0.5rem' : '1rem',
      fontSize: isMobile ? '14px' : '16px'
    }}>
      محتوا
    </div>
  )
}
```

## Best Practices

1. **استفاده از Theme**: همیشه از Theme استفاده کنید نه مقادیر hard-coded
2. **CSS Variables**: برای مقادیر قابل تغییر از CSS Variables استفاده کنید
3. **Consistency**: از مقادیر Theme برای حفظ یکپارچگی استفاده کنید
4. **Override با احتیاط**: فقط در صورت نیاز Theme را override کنید

## مثال کامل

```jsx
// CustomThemeProvider.jsx
import React, { createContext, useContext, useState } from 'react'
import { themes } from '../ui/theme'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme, themeConfig: themes[theme] }}>
      <div style={{
        backgroundColor: themes[theme].colors.bg,
        color: themes[theme].colors.text,
        minHeight: '100vh'
      }}>
        {children}
      </div>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  return useContext(ThemeContext)
}

// استفاده
function App() {
  return (
    <ThemeProvider>
      <YourApp />
    </ThemeProvider>
  )
}

function YourApp() {
  const { theme, setTheme, themeConfig } = useTheme()
  
  return (
    <div>
      <Button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        تغییر Theme
      </Button>
      <Card style={{ backgroundColor: themeConfig.colors.cardBg }}>
        محتوا
      </Card>
    </div>
  )
}
```

## مراحل بعدی

- [معماری فرانت‌اند](../03-frontend/architecture.md)
- [استایل‌دهی و Theme](../03-frontend/styling-theme.md)

