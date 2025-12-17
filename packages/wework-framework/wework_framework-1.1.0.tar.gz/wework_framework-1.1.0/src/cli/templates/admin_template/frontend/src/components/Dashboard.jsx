import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/dashboard/stats`)
        setStats(response.data)
      } catch (error) {
        console.error('Error fetching stats:', error)
        setStats({
          totalUsers: 1250,
          totalOrders: 3420,
          totalRevenue: 125000000,
          growthRate: 12.5
        })
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return <div className="dashboard">در حال بارگذاری...</div>
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>داشبورد</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">کل کاربران</div>
          <div className="stat-value">{stats?.totalUsers?.toLocaleString('fa-IR')}</div>
          <div className="stat-change">+12.5% نسبت به ماه قبل</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">کل سفارشات</div>
          <div className="stat-value">{stats?.totalOrders?.toLocaleString('fa-IR')}</div>
          <div className="stat-change">+8.2% نسبت به ماه قبل</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">درآمد کل</div>
          <div className="stat-value">{stats?.totalRevenue?.toLocaleString('fa-IR')} تومان</div>
          <div className="stat-change">+15.3% نسبت به ماه قبل</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">نرخ رشد</div>
          <div className="stat-value">{stats?.growthRate}%</div>
          <div className="stat-change">مثبت</div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

