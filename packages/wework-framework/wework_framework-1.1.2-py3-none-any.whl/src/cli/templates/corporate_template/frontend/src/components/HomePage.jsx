import React from 'react'
import { Link } from 'react-router-dom'
import '../App.css'

function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="hero-content">
          <h1>به {{PROJECT_NAME}} خوش آمدید</h1>
          <p>
            ما با ارائه بهترین خدمات و راه‌حل‌های نوین، همراه شما در مسیر موفقیت هستیم
          </p>
          <div className="hero-buttons">
            <Link to="/services" className="btn btn-primary">
              مشاهده خدمات
            </Link>
            <Link to="/contact" className="btn btn-secondary">
              تماس با ما
            </Link>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'white' }}>
        <h2 className="section-title">چرا ما را انتخاب کنید؟</h2>
        <p className="section-subtitle">
          ما با سال‌ها تجربه و تیمی متخصص، بهترین خدمات را به شما ارائه می‌دهیم
        </p>
        <div className="services-grid">
          <div className="service-card">
            <div className="service-icon">✨</div>
            <h3>کیفیت برتر</h3>
            <p>
              ارائه خدمات با بالاترین استانداردهای کیفیت و رضایت کامل مشتریان
            </p>
          </div>
          <div className="service-card">
            <div className="service-icon">🚀</div>
            <h3>عملکرد سریع</h3>
            <p>
              سرعت بالا در ارائه خدمات و پاسخگویی سریع به نیازهای شما
            </p>
          </div>
          <div className="service-card">
            <div className="service-icon">💎</div>
            <h3>قیمت مناسب</h3>
            <p>
              بهترین قیمت‌ها با کیفیت عالی و خدمات پس از فروش
            </p>
          </div>
        </div>
      </section>
    </>
  )
}

export default HomePage

