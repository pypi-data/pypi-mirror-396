import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import AdminDashboard from './AdminDashboard'
import AdminUsers from './AdminUsers'
import '../App.css'

function AdminPanel() {
  const location = useLocation()

  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar open">
        <div className="dashboard-sidebar-header">
          <h2 style={{ color: 'white' }}>پنل مدیریت</h2>
        </div>
        <nav className="dashboard-sidebar-menu">
          <Link
            to="/admin"
            className={`dashboard-sidebar-link ${location.pathname === '/admin' ? 'active' : ''}`}
          >
            داشبورد
          </Link>
          <Link
            to="/admin/users"
            className={`dashboard-sidebar-link ${location.pathname === '/admin/users' ? 'active' : ''}`}
          >
            مدیریت کاربران
          </Link>
        </nav>
      </aside>
      <main className="dashboard-content">
        <Routes>
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<AdminUsers />} />
        </Routes>
      </main>
    </div>
  )
}

export default AdminPanel

