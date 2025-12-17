import React from 'react'
import './Badge.css'

/**
 * Badge Component - Status indicator
 * @param {string} variant - 'success' | 'error' | 'warning' | 'info' | 'muted'
 * @param {string} size - 'sm' | 'md' | 'lg'
 * @param {string} className - Additional classes
 * @param {React.ReactNode} children - Badge content
 * @param {object} ...props - Other span props
 */
export const Badge = ({
  variant = 'info',
  size = 'md',
  className = '',
  children,
  ...props
}) => {
  const classes = [
    'ui-badge',
    `ui-badge--${variant}`,
    `ui-badge--${size}`,
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <span className={classes} {...props}>
      {children}
    </span>
  )
}

export default Badge

