# استایل‌دهی و Theme

این سند نحوه استایل‌دهی و استفاده از Theme در فرانت‌اند را توضیح می‌دهد.

## CSS Modules

```jsx
// MyComponent.module.css
.container {
  padding: 1rem;
  background: #fff;
}

// MyComponent.jsx
import styles from './MyComponent.module.css'

function MyComponent() {
  return <div className={styles.container}>Content</div>
}
```

## Theme System

```jsx
import { theme } from '../ui/theme'

const style = {
  color: theme.colors.primary,
  padding: theme.spacing.md
}
```

## CSS Variables

```css
:root {
  --color-primary: #007bff;
  --spacing-md: 1rem;
}

.my-component {
  color: var(--color-primary);
  padding: var(--spacing-md);
}
```

## مراحل بعدی

- [معماری فرانت‌اند](./architecture.md)
- [UI Kit](../04-ui-kit/introduction.md)

