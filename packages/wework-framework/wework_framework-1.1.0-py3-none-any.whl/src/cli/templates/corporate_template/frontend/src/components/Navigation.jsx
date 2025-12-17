import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import '../App.css'

function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="nav">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          {{PROJECT_NAME}}
        </Link>
        <button
          className="nav-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? '✕' : '☰'}
        </button>
        <ul className={`nav-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <li>
            <Link
              to="/"
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              خانه
            </Link>
          </li>
          <li>
            <Link
              to="/services"
              className={`nav-link ${isActive('/services') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              خدمات
            </Link>
          </li>
          <li>
            <Link
              to="/about"
              className={`nav-link ${isActive('/about') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              درباره ما
            </Link>
          </li>
          <li>
            <Link
              to="/contact"
              className={`nav-link ${isActive('/contact') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              تماس با ما
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navigation

