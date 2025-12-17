# Hooks و Utilities

این سند Custom Hooks و Utilities موجود در فریمورک WeWork را توضیح می‌دهد.

## Custom Hooks

### useInfiniteScroll

```jsx
import { useInfiniteScroll } from '../hooks/useInfiniteScroll'

function InfiniteList() {
  const { lastElementRef } = useInfiniteScroll(
    loadMore,
    hasMore,
    loading
  )
  
  return (
    <div>
      {items.map((item, index) => (
        <div
          key={item.id}
          ref={index === items.length - 1 ? lastElementRef : null}
        >
          {item.name}
        </div>
      ))}
    </div>
  )
}
```

### useResponsive

```jsx
import { useResponsive } from '../hooks/useResponsive'

function MyComponent() {
  const { isMobile, isTablet, isDesktop, width } = useResponsive()
  
  return (
    <div>
      {isMobile && <MobileView />}
      {isDesktop && <DesktopView />}
    </div>
  )
}
```

### useHistory

```jsx
import { useHistory } from '../hooks/useHistory'

function MyComponent() {
  const { history, push, back } = useHistory()
  
  return (
    <div>
      <button onClick={() => push('/page')}>Go</button>
      <button onClick={back}>Back</button>
    </div>
  )
}
```

## Utilities

### dateUtils

```jsx
import { formatDate, formatTime, formatDateTime } from '../utils/dateUtils'

const date = new Date()
formatDate(date)  // "1403/01/15"
formatTime(date)  // "14:30"
formatDateTime(date)  // "1403/01/15 14:30"
```

## مراحل بعدی

- [معماری فرانت‌اند](./architecture.md)
- [استایل‌دهی و Theme](./styling-theme.md)

