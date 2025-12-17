import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { useCart } from '../App'
import '../App.css'

function ProductDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [quantity, setQuantity] = useState(1)
  const { addToCart } = useCart()

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/products/${id}`)
        setProduct(response.data)
      } catch (error) {
        console.error('Error fetching product:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id])

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
      addToCart(product)
    }
    navigate('/cart')
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', marginTop: '100px' }}>در حال بارگذاری...</div>
  }

  if (!product) {
    return <div style={{ textAlign: 'center', padding: '3rem', marginTop: '100px' }}>محصول یافت نشد</div>
  }

  return (
    <div className="product-detail">
      <img
        src={product.image_url || 'https://via.placeholder.com/600'}
        alt={product.name}
        className="product-detail-image"
      />
      <div className="product-detail-info">
        <h1>{product.name}</h1>
        <div className="product-detail-price">
          {product.price.toLocaleString('fa-IR')} تومان
        </div>
        <p className="product-detail-description">
          {product.description || 'توضیحات محصول'}
        </p>
        <div style={{ marginBottom: '1rem' }}>
          <label>تعداد: </label>
          <input
            type="number"
            min="1"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
            style={{
              width: '80px',
              padding: '0.5rem',
              border: '2px solid #e2e8f0',
              borderRadius: '8px',
              marginRight: '1rem'
            }}
          />
        </div>
        <button className="btn-primary" onClick={handleAddToCart}>
          افزودن به سبد خرید
        </button>
      </div>
    </div>
  )
}

export default ProductDetailPage

