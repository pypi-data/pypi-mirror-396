import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../App'
import '../App.css'

function CheckoutPage() {
  const { cart, getCartTotal } = useCart()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: ''
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      setLoading(false)
      alert('سفارش شما با موفقیت ثبت شد!')
      navigate('/')
    }, 1000)
  }

  if (cart.length === 0) {
    navigate('/cart')
    return null
  }

  return (
    <form className="checkout-form" onSubmit={handleSubmit}>
      <h1 style={{ marginBottom: '2rem' }}>تکمیل اطلاعات</h1>
      <div className="form-group">
        <label>نام و نام خانوادگی *</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label>ایمیل *</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label>شماره تماس *</label>
        <input
          type="tel"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label>آدرس *</label>
        <input
          type="text"
          name="address"
          value={formData.address}
          onChange={handleChange}
          required
        />
      </div>
      <div style={{
        background: '#f1f5f9',
        padding: '1.5rem',
        borderRadius: '10px',
        marginBottom: '1.5rem'
      }}>
        <h3>جمع کل: {getCartTotal().toLocaleString('fa-IR')} تومان</h3>
      </div>
      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? 'در حال پردازش...' : 'تایید و پرداخت'}
      </button>
    </form>
  )
}

export default CheckoutPage

