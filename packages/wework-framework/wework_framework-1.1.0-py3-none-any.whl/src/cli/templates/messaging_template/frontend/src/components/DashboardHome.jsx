import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function DashboardHome() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/stats`, {
          params: { user_id: 1 }
        })
        setStats(response.data)
      } catch (error) {
        console.error('Error fetching stats:', error)
        setStats({
          total_accounts: 0,
          total_campaigns: 0,
          total_messages_sent: 0,
          success_rate: 0,
          active_subscription: false
        })
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return <div>در حال بارگذاری...</div>
  }

  return (
    <div>
      <div className="dashboard-header">
        <h1>داشبورد</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">اکانت‌های متصل</div>
          <div className="stat-value">{stats?.total_accounts || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">کمپین‌های ارسال</div>
          <div className="stat-value">{stats?.total_campaigns || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">پیام‌های ارسال شده</div>
          <div className="stat-value">{stats?.total_messages_sent?.toLocaleString('fa-IR') || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">نرخ موفقیت</div>
          <div className="stat-value">{stats?.success_rate || 0}%</div>
        </div>
      </div>
      <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <Link to="/dashboard/accounts" className="btn btn-primary">
          مدیریت اکانت‌ها
        </Link>
        <Link to="/dashboard/campaigns/new" className="btn btn-primary">
          ایجاد کمپین جدید
        </Link>
      </div>
    </div>
  )
}

export default DashboardHome

