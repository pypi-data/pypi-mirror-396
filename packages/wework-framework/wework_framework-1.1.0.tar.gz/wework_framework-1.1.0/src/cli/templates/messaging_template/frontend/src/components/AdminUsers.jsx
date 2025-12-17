import React from 'react'
import '../App.css'

function AdminUsers() {
  const users = [
    { id: 1, name: 'کاربر 1', email: 'user1@example.com', accounts: 2, campaigns: 5, status: 'active' },
    { id: 2, name: 'کاربر 2', email: 'user2@example.com', accounts: 1, campaigns: 2, status: 'active' },
    { id: 3, name: 'کاربر 3', email: 'user3@example.com', accounts: 3, campaigns: 8, status: 'inactive' }
  ]

  return (
    <div>
      <div className="dashboard-header">
        <h1>مدیریت کاربران</h1>
      </div>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>شناسه</th>
              <th>نام</th>
              <th>ایمیل</th>
              <th>تعداد اکانت‌ها</th>
              <th>تعداد کمپین‌ها</th>
              <th>وضعیت</th>
              <th>عملیات</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.accounts}</td>
                <td>{user.campaigns}</td>
                <td>
                  <span className={`account-badge ${user.status === 'active' ? 'active' : 'inactive'}`}>
                    {user.status === 'active' ? 'فعال' : 'غیرفعال'}
                  </span>
                </td>
                <td>
                  <button style={{
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}>
                    مشاهده جزئیات
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AdminUsers

