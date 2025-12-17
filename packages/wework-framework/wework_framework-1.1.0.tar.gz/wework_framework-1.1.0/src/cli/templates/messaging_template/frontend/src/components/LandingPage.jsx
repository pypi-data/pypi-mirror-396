import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function LandingPage() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/plans`)
        setPlans(response.data.plans || [])
      } catch (error) {
        console.error('Error fetching plans:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPlans()
  }, [])

  const handlePurchase = (planId) => {
    // In real implementation, redirect to payment gateway
    alert(`خرید پلن ${planId} - در حال انتقال به درگاه پرداخت...`)
  }

  return (
    <div className="landing">
      <nav className="landing-nav">
        <Link to="/" className="landing-logo">
          {{PROJECT_NAME}}
        </Link>
        <div className="landing-nav-buttons">
          <Link to="/dashboard" className="btn btn-outline">
            ورود
          </Link>
          <Link to="/dashboard" className="btn btn-primary">
            شروع کنید
          </Link>
        </div>
      </nav>

      <section className="hero">
        <h1>سامانه ارسال پیام در پیام‌رسان‌های ایرانی</h1>
        <p>
          ارسال پیام به صورت توزیع شده بین چندین اکانت پیام‌رسان
          <br />
          پشتیبانی از بله، ایتا، روبیکا، سروش، گپ و سایر پیام‌رسان‌های ایرانی
        </p>
        <div>
          <Link to="/dashboard" className="btn btn-primary" style={{ marginLeft: '1rem' }}>
            شروع کنید
          </Link>
          <a href="#plans" className="btn btn-outline">
            مشاهده پلن‌ها
          </a>
        </div>
      </section>

      <section id="plans" className="plans-section">
        <h2 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '1rem', color: '#1e293b' }}>
          انتخاب پلن مناسب
        </h2>
        <p style={{ textAlign: 'center', color: '#64748b', marginBottom: '3rem' }}>
          پلن مورد نظر خود را انتخاب کنید و شروع به ارسال پیام کنید
        </p>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>در حال بارگذاری...</div>
        ) : (
          <div className="plans-grid">
            {plans.map((plan, index) => (
              <div
                key={plan.id}
                className={`plan-card ${index === 1 ? 'featured' : ''}`}
              >
                {index === 1 && <div className="plan-badge">محبوب‌ترین</div>}
                <div className="plan-name">{plan.name}</div>
                <div className="plan-price">
                  {plan.price.toLocaleString('fa-IR')} تومان
                </div>
                <div className="plan-duration">برای {plan.duration_days} روز</div>
                <ul className="plan-features">
                  <li>تا {plan.max_accounts} اکانت پیام‌رسان</li>
                  <li>تا {plan.max_messages_per_day.toLocaleString('fa-IR')} پیام در روز</li>
                  {plan.features?.support && (
                    <li>پشتیبانی: {plan.features.support}</li>
                  )}
                  {plan.features?.api_access && (
                    <li>✓ دسترسی به API</li>
                  )}
                </ul>
                <button
                  className="btn btn-primary"
                  onClick={() => handlePurchase(plan.id)}
                  style={{ width: '100%' }}
                >
                  خرید اشتراک
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default LandingPage

