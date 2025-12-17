import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      await axios.post(`${API_BASE_URL}/contact`, formData)
      setSuccess(true)
      setFormData({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
      })
    } catch (err) {
      setError('خطا در ارسال پیام. لطفاً دوباره تلاش کنید.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ paddingTop: '80px', minHeight: '100vh', background: 'white' }}>
      <section className="section">
        <h2 className="section-title">تماس با ما</h2>
        <p className="section-subtitle">
          ما آماده پاسخگویی به سوالات و دریافت نظرات شما هستیم
        </p>
        <form className="contact-form" onSubmit={handleSubmit}>
          {success && (
            <div style={{
              background: '#10b981',
              color: 'white',
              padding: '1rem',
              borderRadius: '10px',
              marginBottom: '1.5rem',
              textAlign: 'center'
            }}>
              پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.
            </div>
          )}
          {error && (
            <div style={{
              background: '#ef4444',
              color: 'white',
              padding: '1rem',
              borderRadius: '10px',
              marginBottom: '1.5rem',
              textAlign: 'center'
            }}>
              {error}
            </div>
          )}
          <div className="form-group">
            <label htmlFor="name">نام و نام خانوادگی *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="email">ایمیل *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="phone">شماره تماس</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="subject">موضوع</label>
            <input
              type="text"
              id="subject"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="message">پیام *</label>
            <textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? 'در حال ارسال...' : 'ارسال پیام'}
          </button>
        </form>
      </section>
    </div>
  )
}

export default ContactPage

