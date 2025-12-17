# Routing و Navigation

این سند نحوه استفاده از Routing در فرانت‌اند فریمورک WeWork را توضیح می‌دهد.

## React Router

### Setup

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
```

## Protected Routes

```jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  
  return children
}

// استفاده
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

## Navigation

```jsx
import { useNavigate, useParams, Link } from 'react-router-dom'

function MyComponent() {
  const navigate = useNavigate()
  const { id } = useParams()
  
  const handleClick = () => {
    navigate('/products')
  }
  
  return (
    <div>
      <Link to="/products">Products</Link>
      <button onClick={handleClick}>Go to Products</button>
    </div>
  )
}
```

## مراحل بعدی

- [معماری فرانت‌اند](./architecture.md)
- [Hooks و Utilities](./hooks-utils.md)

