import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function AccountsPage() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    messenger_type: 'bale',
    account_name: '',
    account_phone: ''
  })

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/1/accounts`)
      setAccounts(response.data.accounts || [])
    } catch (error) {
      console.error('Error fetching accounts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddAccount = async (e) => {
    e.preventDefault()
    try {
      await axios.post(`${API_BASE_URL}/users/1/accounts`, formData)
      setShowAddForm(false)
      setFormData({ messenger_type: 'bale', account_name: '', account_phone: '' })
      fetchAccounts()
    } catch (error) {
      console.error('Error adding account:', error)
      alert('خطا در افزودن اکانت')
    }
  }

  const handleDelete = async (accountId) => {
    if (!confirm('آیا از حذف این اکانت اطمینان دارید؟')) return
    try {
      await axios.delete(`${API_BASE_URL}/accounts/${accountId}`)
      fetchAccounts()
    } catch (error) {
      console.error('Error deleting account:', error)
    }
  }

  const messengerNames = {
    bale: 'بله',
    eita: 'ایتا',
    rubika: 'روبیکا',
    soroush: 'سروش',
    gap: 'گپ'
  }

  return (
    <div>
      <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>مدیریت اکانت‌های پیام‌رسان</h1>
        <button className="btn btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'انصراف' : 'افزودن اکانت جدید'}
        </button>
      </div>

      {showAddForm && (
        <div className="campaign-form" style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1.5rem' }}>افزودن اکانت جدید</h2>
          <form onSubmit={handleAddAccount}>
            <div className="form-group">
              <label>نوع پیام‌رسان</label>
              <select
                value={formData.messenger_type}
                onChange={(e) => setFormData({ ...formData, messenger_type: e.target.value })}
                required
              >
                <option value="bale">بله</option>
                <option value="eita">ایتا</option>
                <option value="rubika">روبیکا</option>
                <option value="soroush">سروش</option>
                <option value="gap">گپ</option>
              </select>
            </div>
            <div className="form-group">
              <label>نام اکانت</label>
              <input
                type="text"
                value={formData.account_name}
                onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>شماره تماس (اختیاری)</label>
              <input
                type="tel"
                value={formData.account_phone}
                onChange={(e) => setFormData({ ...formData, account_phone: e.target.value })}
              />
            </div>
            <button type="submit" className="btn btn-primary">
              افزودن اکانت
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div>در حال بارگذاری...</div>
      ) : accounts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '10px' }}>
          <p>هیچ اکانتی اضافه نشده است</p>
          <button className="btn btn-primary" onClick={() => setShowAddForm(true)} style={{ marginTop: '1rem' }}>
            افزودن اولین اکانت
          </button>
        </div>
      ) : (
        <div>
          {accounts.map((account) => (
            <div key={account.id} className="account-card">
              <div className="account-info">
                <h3>{account.account_name}</h3>
                <p>
                  {messengerNames[account.messenger_type] || account.messenger_type}
                  {account.account_phone && ` - ${account.account_phone}`}
                </p>
              </div>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <span className={`account-badge ${account.is_active ? 'active' : 'inactive'}`}>
                  {account.is_active ? 'فعال' : 'غیرفعال'}
                </span>
                <button
                  onClick={() => handleDelete(account.id)}
                  style={{
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  حذف
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AccountsPage

