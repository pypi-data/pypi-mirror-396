import React from 'react'
import { Link } from 'react-router-dom'
import '../App.css'

function HomePage() {
  return (
    <>
      <section className="hero">
        <h1>به فروشگاه {{PROJECT_NAME}} خوش آمدید</h1>
        <p>بهترین محصولات با بهترین قیمت‌ها</p>
        <Link to="/products" className="btn-primary" style={{ marginTop: '2rem', display: 'inline-block', textDecoration: 'none' }}>
          مشاهده محصولات
        </Link>
      </section>
    </>
  )
}

export default HomePage

