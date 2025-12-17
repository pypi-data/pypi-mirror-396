import React from 'react'
import '../App.css'

function AdminDashboard() {
  return (
    <div>
      <div className="dashboard-header">
        <h1>داشبورد مدیریت</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">کل کاربران</div>
          <div className="stat-value">1,250</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">اشتراک‌های فعال</div>
          <div className="stat-value">890</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">پیام‌های ارسال شده امروز</div>
          <div className="stat-value">45,230</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">درآمد ماهانه</div>
          <div className="stat-value">125,000,000 تومان</div>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard

