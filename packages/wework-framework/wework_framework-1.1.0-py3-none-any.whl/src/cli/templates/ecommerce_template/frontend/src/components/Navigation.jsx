import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useCart } from '../App'
import '../App.css'

function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { getCartCount } = useCart()
  const location = useLocation()

  return (
    <nav className="nav">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          {{PROJECT_NAME}}
        </Link>
        <button
          className="nav-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? '✕' : '☰'}
        </button>
        <ul className={`nav-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <li>
            <Link
              to="/"
              className="nav-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              خانه
            </Link>
          </li>
          <li>
            <Link
              to="/products"
              className="nav-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              محصولات
            </Link>
          </li>
          <li>
            <Link
              to="/cart"
              className="cart-icon"
              onClick={() => setMobileMenuOpen(false)}
            >
              سبد خرید
              {getCartCount() > 0 && (
                <span className="cart-badge">{getCartCount()}</span>
              )}
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navigation

