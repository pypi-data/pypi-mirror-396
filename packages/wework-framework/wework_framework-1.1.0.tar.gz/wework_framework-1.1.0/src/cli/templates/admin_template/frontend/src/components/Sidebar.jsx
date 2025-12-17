import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import '../App.css'

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation()

  return (
    <>
      <button className="sidebar-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '✕' : '☰'}
      </button>
      <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">{{PROJECT_NAME}}</div>
        </div>
        <nav className="sidebar-menu">
          <Link
            to="/"
            className={`sidebar-link ${location.pathname === '/' ? 'active' : ''}`}
            onClick={() => setIsOpen(false)}
          >
            داشبورد
          </Link>
          <Link
            to="/users"
            className={`sidebar-link ${location.pathname === '/users' ? 'active' : ''}`}
            onClick={() => setIsOpen(false)}
          >
            کاربران
          </Link>
        </nav>
      </aside>
    </>
  )
}

export default Sidebar

