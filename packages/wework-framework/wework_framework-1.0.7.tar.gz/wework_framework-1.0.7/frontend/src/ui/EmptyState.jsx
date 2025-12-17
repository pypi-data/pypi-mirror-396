import React from 'react'
import './EmptyState.css'

/**
 * EmptyState Component - Display when no data available
 * @param {string} title - Empty state title
 * @param {string} description - Empty state description
 * @param {React.ReactNode} icon - Optional icon
 * @param {React.ReactNode} action - Optional action button
 */
export const EmptyState = ({
  title = 'داده‌ای وجود ندارد',
  description,
  icon,
  action,
  className = '',
}) => {
  return (
    <div className={`ui-empty-state ${className}`}>
      {icon && <div className="ui-empty-state-icon">{icon}</div>}
      <h3 className="ui-empty-state-title">{title}</h3>
      {description && (
        <p className="ui-empty-state-description">{description}</p>
      )}
      {action && <div className="ui-empty-state-action">{action}</div>}
    </div>
  )
}

export default EmptyState

