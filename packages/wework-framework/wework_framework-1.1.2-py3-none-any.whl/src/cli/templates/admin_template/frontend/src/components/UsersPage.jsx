import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function UsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/users`, {
          params: { page, limit: 10, search }
        })
        setUsers(response.data.users || [])
      } catch (error) {
        console.error('Error fetching users:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [page, search])

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>مدیریت کاربران</h1>
      </div>
      <div className="table-container">
        <div className="table-header">
          <input
            type="text"
            placeholder="جستجوی کاربر..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>در حال بارگذاری...</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>شناسه</th>
                <th>نام</th>
                <th>ایمیل</th>
                <th>نقش</th>
                <th>وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.name}</td>
                  <td>{user.email}</td>
                  <td>{user.role}</td>
                  <td>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      borderRadius: '20px',
                      background: user.status === 'active' ? '#d1fae5' : '#fee2e2',
                      color: user.status === 'active' ? '#065f46' : '#991b1b',
                      fontSize: '0.875rem'
                    }}>
                      {user.status === 'active' ? 'فعال' : 'غیرفعال'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default UsersPage

