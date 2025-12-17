import React from 'react'
import './Table.css'

/**
 * Table Component - Responsive table with mobile card view
 * @param {array} columns - Column definitions [{ key, label, render?, mobileLabel? }]
 * @param {array} data - Table data
 * @param {function} renderMobileCard - Custom mobile card renderer
 * @param {string} className - Additional classes
 */
export const Table = ({
  columns = [],
  data = [],
  renderMobileCard,
  className = '',
  emptyMessage = 'داده‌ای برای نمایش وجود ندارد',
  ...props
}) => {
  if (data.length === 0) {
    return (
      <div className="ui-table-empty">
        <p>{emptyMessage}</p>
      </div>
    )
  }

  return (
    <>
      {/* Desktop Table View */}
      <div className="ui-table-wrapper ui-table-desktop">
        <table className={`ui-table ${className}`} {...props}>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key} className={col.className || ''}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={row.id || idx}>
                {columns.map((col) => (
                  <td key={col.key} className={col.className || ''}>
                    {col.render
                      ? col.render(row[col.key], row, idx)
                      : row[col.key] ?? '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View */}
      <div className="ui-table-mobile">
        {data.map((row, idx) => {
          if (renderMobileCard) {
            return <React.Fragment key={row.id || idx}>{renderMobileCard(row, idx)}</React.Fragment>
          }
          return (
            <div key={row.id || idx} className="ui-table-card">
              {columns.map((col) => {
                const value = col.render
                  ? col.render(row[col.key], row, idx)
                  : row[col.key] ?? '—'
                const label = col.mobileLabel || col.label
                return (
                  <div key={col.key} className="ui-table-card-row">
                    <span className="ui-table-card-label">{label}</span>
                    <span className="ui-table-card-value">{value}</span>
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>
    </>
  )
}

export default Table

