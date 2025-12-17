# مدیریت State

این سند نحوه مدیریت State در فرانت‌اند فریمورک WeWork را توضیح می‌دهد.

## Local State

### useState

```jsx
import { useState } from 'react'

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

## Context API

### ایجاد Context

```jsx
// AuthContext.jsx
import { createContext, useContext, useState } from 'react'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  
  const login = async (email, password) => {
    // Login logic
    const response = await loginAPI(email, password)
    setToken(response.token)
    setUser(response.user)
    localStorage.setItem('token', response.token)
  }
  
  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
  }
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
```

### استفاده

```jsx
import { useAuth } from './AuthContext'

function MyComponent() {
  const { user, login, logout } = useAuth()
  
  return (
    <div>
      {user ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={() => login('email', 'password')}>Login</button>
      )}
    </div>
  )
}
```

## React Query

### استفاده

```jsx
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'

function ProductsList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const res = await axios.get('/api/products')
      return res.data
    }
  })
  
  const mutation = useMutation({
    mutationFn: async (product) => {
      const res = await axios.post('/api/products', product)
      return res.data
    }
  })
  
  if (isLoading) return <Loading />
  if (error) return <Error message={error.message} />
  
  return (
    <div>
      {data.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}
```

## Best Practices

1. **Local State برای داده‌های ساده**
2. **Context برای داده‌های global**
3. **React Query برای server state**
4. **Avoid prop drilling**: از Context استفاده کنید

## مراحل بعدی

- [معماری فرانت‌اند](./architecture.md)
- [Routing و Navigation](./routing.md)

