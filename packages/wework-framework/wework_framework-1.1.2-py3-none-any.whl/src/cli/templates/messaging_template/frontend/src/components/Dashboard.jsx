import React, { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import DashboardHome from './DashboardHome'
import AccountsPage from './AccountsPage'
import CampaignsPage from './CampaignsPage'
import NewCampaignPage from './NewCampaignPage'
import '../App.css'

function Dashboard() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="dashboard-layout">
      <aside className={`dashboard-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="dashboard-sidebar-header">
          <h2 style={{ color: 'white' }}>{{PROJECT_NAME}}</h2>
        </div>
        <nav className="dashboard-sidebar-menu">
          <Link
            to="/dashboard"
            className={`dashboard-sidebar-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
          >
            داشبورد
          </Link>
          <Link
            to="/dashboard/accounts"
            className={`dashboard-sidebar-link ${location.pathname === '/dashboard/accounts' ? 'active' : ''}`}
          >
            اکانت‌های پیام‌رسان
          </Link>
          <Link
            to="/dashboard/campaigns"
            className={`dashboard-sidebar-link ${location.pathname.includes('/dashboard/campaigns') ? 'active' : ''}`}
          >
            کمپین‌های ارسال
          </Link>
          <Link
            to="/dashboard/campaigns/new"
            className={`dashboard-sidebar-link ${location.pathname === '/dashboard/campaigns/new' ? 'active' : ''}`}
          >
            ایجاد کمپین جدید
          </Link>
        </nav>
      </aside>
      <main className="dashboard-content">
        <Routes>
          <Route index element={<DashboardHome />} />
          <Route path="accounts" element={<AccountsPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="campaigns/new" element={<NewCampaignPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default Dashboard

