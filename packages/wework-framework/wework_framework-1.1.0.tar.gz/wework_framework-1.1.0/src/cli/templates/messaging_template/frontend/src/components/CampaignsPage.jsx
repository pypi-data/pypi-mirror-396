import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/campaigns`, {
        params: { user_id: 1 }
      })
      setCampaigns(response.data.campaigns || [])
    } catch (error) {
      console.error('Error fetching campaigns:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981'
      case 'sending':
        return '#3b82f6'
      case 'failed':
        return '#ef4444'
      default:
        return '#64748b'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'تکمیل شده'
      case 'sending':
        return 'در حال ارسال'
      case 'failed':
        return 'ناموفق'
      default:
        return 'در انتظار'
    }
  }

  return (
    <div>
      <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>کمپین‌های ارسال</h1>
        <Link to="/dashboard/campaigns/new" className="btn btn-primary">
          ایجاد کمپین جدید
        </Link>
      </div>

      {loading ? (
        <div>در حال بارگذاری...</div>
      ) : campaigns.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '10px' }}>
          <p>هیچ کمپینی ایجاد نشده است</p>
          <Link to="/dashboard/campaigns/new" className="btn btn-primary" style={{ marginTop: '1rem', display: 'inline-block' }}>
            ایجاد اولین کمپین
          </Link>
        </div>
      ) : (
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>نام کمپین</th>
                <th>وضعیت</th>
                <th>کل گیرندگان</th>
                <th>ارسال شده</th>
                <th>ناموفق</th>
                <th>تاریخ ایجاد</th>
                <th>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td>{campaign.name}</td>
                  <td>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      borderRadius: '20px',
                      background: getStatusColor(campaign.status) + '20',
                      color: getStatusColor(campaign.status),
                      fontSize: '0.875rem',
                      fontWeight: '600'
                    }}>
                      {getStatusText(campaign.status)}
                    </span>
                  </td>
                  <td>{campaign.total_recipients}</td>
                  <td>{campaign.sent_count}</td>
                  <td>{campaign.failed_count}</td>
                  <td>{new Date(campaign.created_at).toLocaleDateString('fa-IR')}</td>
                  <td>
                    <Link
                      to={`/dashboard/campaigns/${campaign.id}`}
                      style={{ color: '#3b82f6', textDecoration: 'none' }}
                    >
                      مشاهده جزئیات
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default CampaignsPage

