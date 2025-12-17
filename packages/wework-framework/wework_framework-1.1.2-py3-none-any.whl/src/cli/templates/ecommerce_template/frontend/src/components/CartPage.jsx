import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../App'
import '../App.css'

function CartPage() {
  const { cart, removeFromCart, updateQuantity, getCartTotal } = useCart()
  const navigate = useNavigate()

  if (cart.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', marginTop: '100px' }}>
        <h2>سبد خرید شما خالی است</h2>
        <button
          className="btn-primary"
          onClick={() => navigate('/products')}
          style={{ marginTop: '2rem', maxWidth: '300px' }}
        >
          مشاهده محصولات
        </button>
      </div>
    )
  }

  return (
    <div className="cart-page">
      <h1 style={{ marginBottom: '2rem' }}>سبد خرید</h1>
      {cart.map((item) => (
        <div key={item.id} className="cart-item">
          <img
            src={item.image_url || 'https://via.placeholder.com/100'}
            alt={item.name}
            className="cart-item-image"
          />
          <div className="cart-item-info">
            <h3 className="cart-item-name">{item.name}</h3>
            <div className="cart-item-price">
              {(item.price * item.quantity).toLocaleString('fa-IR')} تومان
            </div>
          </div>
          <div className="quantity-controls">
            <button
              className="quantity-btn"
              onClick={() => updateQuantity(item.id, item.quantity - 1)}
            >
              −
            </button>
            <span style={{ fontSize: '1.2rem', fontWeight: '600' }}>
              {item.quantity}
            </span>
            <button
              className="quantity-btn"
              onClick={() => updateQuantity(item.id, item.quantity + 1)}
            >
              +
            </button>
          </div>
          <button
            onClick={() => removeFromCart(item.id)}
            style={{
              background: '#ef4444',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            حذف
          </button>
        </div>
      ))}
      <div className="cart-total">
        <h2>جمع کل: <span className="total-price">{getCartTotal().toLocaleString('fa-IR')} تومان</span></h2>
        <button
          className="btn-primary"
          onClick={() => navigate('/checkout')}
          style={{ marginTop: '1rem' }}
        >
          ادامه به پرداخت
        </button>
      </div>
    </div>
  )
}

export default CartPage

