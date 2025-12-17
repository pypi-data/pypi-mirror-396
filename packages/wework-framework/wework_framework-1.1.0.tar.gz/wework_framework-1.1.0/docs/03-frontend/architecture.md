# معماری فرانت‌اند

این سند معماری فرانت‌اند فریمورک WeWork را توضیح می‌دهد.

## ساختار کلی

```
frontend/
├── src/
│   ├── components/      # کامپوننت‌های اپلیکیشن
│   ├── ui/             # UI Kit
│   ├── hooks/          # Custom Hooks
│   ├── utils/          # Utilities
│   ├── config.js       # تنظیمات
│   ├── App.jsx         # کامپوننت اصلی
│   └── main.jsx        # Entry Point
```

## کامپوننت‌ها

### کامپوننت ساده

```jsx
import React from 'react'

function MyComponent() {
  return <div>Hello</div>
}

export default MyComponent
```

### کامپوننت با State

```jsx
import React, { useState } from 'react'

function MyComponent() {
  const [count, setCount] = useState(0)
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

## Routing

### استفاده از React Router

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  )
}
```

## State Management

### Local State

```jsx
const [state, setState] = useState(initialValue)
```

### Context API

```jsx
// AuthContext.jsx
import { createContext, useContext, useState } from 'react'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  
  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
```

### React Query

```jsx
import { useQuery } from '@tanstack/react-query'

function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: () => fetchItems()
  })
  
  if (isLoading) return <Loading />
  return <div>{data}</div>
}
```

## API Calls

### با Axios

```jsx
import axios from 'axios'
import { API_BASE_URL } from '../config'

async function fetchData() {
  const res = await axios.get(`${API_BASE_URL}/items`)
  return res.data
}
```

### با React Query

```jsx
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

function useItems() {
  return useQuery({
    queryKey: ['items'],
    queryFn: async () => {
      const res = await axios.get(`${API_BASE_URL}/items`)
      return res.data
    }
  })
}
```

## Hooks

### Custom Hook

```jsx
// hooks/useItems.js
import { useState, useEffect } from 'react'
import axios from 'axios'

export function useItems() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchItems()
  }, [])
  
  const fetchItems = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/items`)
      setItems(res.data)
    } finally {
      setLoading(false)
    }
  }
  
  return { items, loading, refetch: fetchItems }
}
```

## مراحل بعدی

- [UI Kit](../04-ui-kit/introduction.md)
- [Routing و Navigation](./routing.md)

