import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function NewCampaignPage() {
  const navigate = useNavigate()
  const [accounts, setAccounts] = useState([])
  const [formData, setFormData] = useState({
    name: '',
    message_text: '',
    recipients: '',
    account_ids: []
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/1/accounts`)
      setAccounts(response.data.accounts || [])
    } catch (error) {
      console.error('Error fetching accounts:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const recipientsList = formData.recipients
        .split('\n')
        .map(r => r.trim())
        .filter(r => r)

      const campaignData = {
        name: formData.name,
        message_text: formData.message_text,
        recipients: recipientsList,
        account_ids: formData.account_ids
      }

      const response = await axios.post(`${API_BASE_URL}/campaigns`, campaignData, {
        params: { user_id: 1 }
      })

      alert('کمپین با موفقیت ایجاد شد!')
      navigate('/dashboard/campaigns')
    } catch (error) {
      console.error('Error creating campaign:', error)
      alert('خطا در ایجاد کمپین')
    } finally {
      setLoading(false)
    }
  }

  const handleAccountToggle = (accountId) => {
    setFormData(prev => ({
      ...prev,
      account_ids: prev.account_ids.includes(accountId)
        ? prev.account_ids.filter(id => id !== accountId)
        : [...prev.account_ids, accountId]
    }))
  }

  return (
    <div>
      <div className="dashboard-header">
        <h1>ایجاد کمپین جدید</h1>
      </div>

      <form className="campaign-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>نام کمپین *</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            placeholder="مثلاً: کمپین تبلیغاتی بهمن ماه"
          />
        </div>

        <div className="form-group">
          <label>متن پیام *</label>
          <textarea
            value={formData.message_text}
            onChange={(e) => setFormData({ ...formData, message_text: e.target.value })}
            required
            placeholder="متن پیامی که می‌خواهید ارسال شود..."
          />
        </div>

        <div className="form-group">
          <label>لیست گیرندگان *</label>
          <textarea
            value={formData.recipients}
            onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
            required
            placeholder="هر شماره یا شناسه در یک خط جداگانه"
            style={{ minHeight: '150px' }}
          />
          <small style={{ color: '#64748b', marginTop: '0.5rem', display: 'block' }}>
            هر شماره یا شناسه را در یک خط جداگانه وارد کنید
          </small>
        </div>

        <div className="form-group">
          <label>انتخاب اکانت‌های پیام‌رسان *</label>
          <p style={{ color: '#64748b', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
            پیام‌ها به صورت توزیع شده بین اکانت‌های انتخاب شده ارسال می‌شوند
          </p>
          {accounts.length === 0 ? (
            <p style={{ color: '#ef4444' }}>
              ابتدا باید حداقل یک اکانت پیام‌رسان اضافه کنید
            </p>
          ) : (
            <div className="checkbox-group">
              {accounts.map((account) => (
                <label key={account.id} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={formData.account_ids.includes(account.id)}
                    onChange={() => handleAccountToggle(account.id)}
                  />
                  <span>{account.account_name} ({account.messenger_type})</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {formData.account_ids.length > 0 && formData.recipients && (
          <div style={{
            background: '#f1f5f9',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1.5rem'
          }}>
            <strong>توزیع پیام:</strong>
            <p style={{ marginTop: '0.5rem', color: '#64748b' }}>
              {formData.recipients.split('\n').filter(r => r.trim()).length} گیرنده
              {' '}بین {formData.account_ids.length} اکانت توزیع می‌شود
              {' '}(حدود {Math.ceil(formData.recipients.split('\n').filter(r => r.trim()).length / formData.account_ids.length)} پیام برای هر اکانت)
            </p>
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || accounts.length === 0 || formData.account_ids.length === 0}
          style={{ width: '100%' }}
        >
          {loading ? 'در حال ایجاد...' : 'ایجاد کمپین و شروع ارسال'}
        </button>
      </form>
    </div>
  )
}

export default NewCampaignPage

