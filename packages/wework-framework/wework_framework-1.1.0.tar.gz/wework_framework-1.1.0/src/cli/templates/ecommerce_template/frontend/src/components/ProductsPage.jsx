import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import { useCart } from '../App'
import '../App.css'

function ProductsPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const { addToCart } = useCart()

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/products`, {
          params: { search }
        })
        setProducts(response.data.products || [])
      } catch (error) {
        console.error('Error fetching products:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [search])

  const handleAddToCart = (e, product) => {
    e.stopPropagation()
    addToCart(product)
  }

  return (
    <div style={{ paddingTop: '80px' }}>
      <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 2rem' }}>
        <input
          type="text"
          placeholder="جستجوی محصول..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%',
            padding: '1rem',
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            fontSize: '1rem',
            marginBottom: '2rem'
          }}
        />
      </div>
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>در حال بارگذاری...</div>
      ) : (
        <div className="products-grid">
          {products.map((product) => (
            <div
              key={product.id}
              className="product-card"
              onClick={() => navigate(`/products/${product.id}`)}
            >
              <img
                src={product.image_url || 'https://via.placeholder.com/300'}
                alt={product.name}
                className="product-image"
              />
              <div className="product-info">
                <h3 className="product-name">{product.name}</h3>
                <div className="product-price">
                  {product.price.toLocaleString('fa-IR')} تومان
                </div>
                <button
                  className="btn-add-cart"
                  onClick={(e) => handleAddToCart(e, product)}
                >
                  افزودن به سبد خرید
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProductsPage

